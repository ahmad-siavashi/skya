"""Pluggable decision policies - Skya's extension points.

Three policies, each an abstract base plus at least one reference
implementation:

- :class:`Scheduler` (CPU scheduling within a VM) - :class:`TimeShared`
- :class:`Hypervisor` (VM management on a host) - :class:`SpaceShared`
- :class:`Placement` (mapping VMs to hosts) - :class:`FirstFit`

To experiment with a new algorithm, subclass the relevant abstract base
and implement the marked methods. See the module-level docstring of
:mod:`skya.policies.scheduler`, :mod:`skya.policies.hypervisor`, and
:mod:`skya.policies.placement` for each contract.

To observe a run rather than control it, subclass
:class:`skya.Tracker` (see :mod:`skya.tracker`) - the ready-made
trackers in :mod:`skya.metrics` are examples.
"""

from __future__ import annotations

from skya.policies.hypervisor import Hypervisor, SpaceShared
from skya.policies.placement import FirstFit, Placement
from skya.policies.scheduler import Scheduler, TimeShared

__all__ = [
    "FirstFit",
    "Hypervisor",
    "Placement",
    "Scheduler",
    "SpaceShared",
    "TimeShared",
]
