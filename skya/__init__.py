"""Skya: A cloud simulator for researchers.

Most use cases need only::

    from skya import App, DataCenter, PM, Request, Simulation, Topic, VM
    from skya.policies import FirstFit, SpaceShared, TimeShared

To add a custom algorithm, subclass one of the three policies in
:mod:`skya.policies` (:class:`~skya.policies.Scheduler`,
:class:`~skya.policies.Hypervisor`, :class:`~skya.policies.Placement`)
and pass an instance in place of the default one. To collect custom
metrics, subclass :class:`Tracker`. Optional submodules:
:mod:`skya.metrics` (ready-made trackers), :mod:`skya.power` (per-host
power models), :mod:`skya.network` (a standalone point-to-point link).
"""

from __future__ import annotations

from skya.core import Clock, EventQueue, on
from skya.compare import compare
from skya.models import App, Daemon, DataCenter, PM, Request, VM
from skya.simulation import Simulation
from skya.topics import Topic
from skya.tracker import Tracker

__all__ = [
    "App",
    "Clock",
    "Daemon",
    "DataCenter",
    "EventQueue",
    "PM",
    "Request",
    "Simulation",
    "Topic",
    "Tracker",
    "VM",
    "compare",
    "on",
]
