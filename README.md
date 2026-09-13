# Skya: A cloud simulator for researchers

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Runtime deps](https://img.shields.io/badge/runtime%20deps-stdlib%20only-success)

[![GitHub last commit](https://img.shields.io/github/last-commit/ahmad-siavashi/skya.svg)](https://github.com/ahmad-siavashi/skya)
![GitHub stars](https://img.shields.io/github/stars/ahmad-siavashi/skya?style=social)

Skya simulates **VM placement**, **host-level resource management**,
and **in-guest CPU scheduling and memory allocation**, with
**energy consumption modeling**. It has no runtime dependencies, and
researchers extend it by overriding a single method on a small set
of policies.

The next two sections are all you need to run your first simulation.

## Getting started

```bash
$ git clone https://github.com/ahmad-siavashi/skya.git
$ pip install -e .
$ python examples/basic_simulation.py
```

Requires Python ≥ 3.11.

## Quickstart

```python
from skya import App, DataCenter, PM, Request, Simulation, Topic, VM
from skya.policies import FirstFit, SpaceShared, TimeShared

sim = Simulation(name='Hello', seed=42)

app = sim.create(App, name='Nginx', length=(1, 1, 1))
vm = sim.create(VM, name='Web', cpu=1, ram=1024, scheduler=TimeShared())
vm.run(app)

pm = sim.create(PM, name='HPE', cpu=(2, 2), ram=2048, hypervisor=SpaceShared())
sim.datacenter = sim.create(DataCenter, name='dc', hosts=[pm], placement=FirstFit())
sim.requests = [sim.create(Request, arrival=0, vm=vm)]

@sim.event_queue.on(Topic.VM_ALLOCATE)
def log_alloc(host, vm):
    print(f'placed {vm.name} on {host.name}')

sim.run().report(to_csv='hello.csv')
```

Policies are passed as *instances*. `seed=` controls reproducibility.
The discrete-event loop advances the clock to the next scheduled event
when idle. `App.length` is in CPU cycles, not seconds; `PM.cpu` gives
each core's cycles per time unit.

## Next steps

For customizing a policy, subscribing to events, metrics, comparing
policies, logging, and internals, see
[examples/README.md](examples/README.md).

<details>
<summary>Generating HTML documentation</summary>

```bash
$ pip install -e ".[docs]"
$ pydoctor --project-name skya --html-output ./docs/ --docformat=numpy ./skya/
```

Open `docs/index.html`. Docstrings follow [NumPy style](https://numpydoc.readthedocs.io/en/latest/format.html).

</details>
