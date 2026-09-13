# Guide and reference

This guide covers customizing a policy, subscribing to events,
built-in metrics, comparing policies, logging, and Skya's internals.
See the [main README](../README.md) for installation and a first
simulation.

## Customize a policy

Subclass a reference implementation and override one hook:

| Slot | Where it plugs in | Subclass / override | Example |
|---|---|---|---|
| [`Scheduler`](../skya/policies/scheduler.py) | `VM(scheduler=...)` | `TimeShared` / `share(processes, cores_cycles)` | [custom_scheduler.py](custom_scheduler.py) |
| [`Hypervisor`](../skya/policies/hypervisor.py) | `PM(hypervisor=...)` | `SpaceShared` / `has_capacity(vm)` | [custom_hypervisor.py](custom_hypervisor.py) |
| [`Placement`](../skya/policies/placement.py) | `DataCenter(placement=...)` | `FirstFit` / `select_host(vm)` (or `migrate`) | [custom_placement.py](custom_placement.py), [live_migration.py](live_migration.py) |

```python
# A first-come-first-served scheduler: the first process gets every cycle.
class FCFS(Scheduler):
    def share(self, processes, cores_cycles):
        return [list(cores_cycles)] + [[0] * len(cores_cycles) for _ in processes[1:]]

# A round-robin placement: each VM goes to the next host in turn.
class RoundRobin(Placement):
    def select_host(self, vm):
        hosts = self.datacenter.hosts
        for i in range(len(hosts)):
            host = hosts[(self._next + i) % len(hosts)]
            if all(host.hypervisor.has_capacity(vm)):
                self._next = (self._next + i + 1) % len(hosts)
                return host
        return None
```

You can still override the full methods (`Scheduler.resume`,
`Placement.allocate`, etc.) when one hook is not enough. To collect
metrics, subclass `Tracker`.

## Subscribing to events

```python
from skya import Topic, on

# Class method - picked up by EventQueue.subscribe_all(obj).
class MyTracker(Tracker):
    @on(Topic.VM_ALLOCATE)
    def _record(self, host, vm): ...

# Runtime form.
@sim.event_queue.on(Topic.VM_ALLOCATE)
def log_alloc(host, vm): ...
```

If you subscribe with a plain string that matches no `Topic`, Skya
raises `ValueError` at subscribe time and suggests the closest match.

## Built-in metrics

`skya.metrics` provides ready-made trackers (`Utilization`,
`CompletionTime`, `Concurrency`, `Energy`). Combine them with
`Composite`:

```python
from skya.metrics import Composite, Utilization, CompletionTime, Energy
from skya.power import LinearPower

sim = Simulation(name='Demo', tracker=Composite([Utilization(), CompletionTime(), Energy()]))
pm = sim.create(PM, ..., hypervisor=SpaceShared(), power=LinearPower(idle=100, peak=250))
```

`sim.run().report()` returns dot-namespaced fields like `util.HPE.cpu`,
`complete.p99`, `energy.HPE.kwh`, alongside `request.arrived` /
`accepted` / `rejected` / `pending`.

## Comparing policies

```python
from skya import compare

rows = compare(
    build_workload,
    seed=42,
    processes=4,
    placement_class=[FirstFit, MyPlacement],
    to_csv='sweep.csv'
)
```

`rows` is a list of plain dicts. Pass it to `pandas.DataFrame(...)`
yourself if you need one.

## Logging

Every line has the form `{Sim@time} {topic} key=value …`:

```
Hello@0 sim.start
Hello@0 request.arrive vm=Web
Hello@0 vm.allocate host=HPE vm=Web
Hello@1 app.start vm=Web app=Nginx
Hello@2 app.stop vm=Web app=Nginx
Hello@3 sim.report request.arrived=1 request.accepted=1 request.rejected=0 request.pending=0
```

Output uses the standard `logging` module, on the logger `skya.<simulation_name>`.

## Architecture

Hybrid discrete-time / discrete-event model. Workloads consume cycles
at each time step. Allocations, lifecycle markers, and custom topics
are dispatched through a per-simulation event queue (the future event
list). Scheduler ticks fire only `clock_resolution` units after the
last tick; an event landing between two ticks is drained at its own
time instead of forcing an extra, zero-work tick.

The clock still advances at most one `clock_resolution` unit per
step, so a long idle stretch costs one step per `clock_resolution`
units (one step per unit at the default `clock_resolution=1`). Every
tick while VMs are running also runs every scheduler, so cost there
scales with the number of concurrent VMs too. Set
`clock_resolution` to match the workload's time resolution (for
example, `300` for 5-minute Azure v2 traces) to cut the step count
down toward `O(events)`. Results are bit-identical to
`clock_resolution=1` when every event time is a multiple of the
resolution.

Two building blocks: a per-simulation `Clock` and `EventQueue`
(`../skya/core/`).
