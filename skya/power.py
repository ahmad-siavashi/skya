"""Per-host power models.

A :class:`PowerModel` predicts the instantaneous power draw of a
:class:`skya.models.PM` given its current CPU utilization. The default
:class:`LinearPower` is the standard reference model used in most
cloud-power-related papers - power scales linearly between the host's
idle and peak draw with utilization.

The :class:`skya.metrics.Energy` tracker samples every host's model on
each :data:`Topic.SIM_TICK`, using ``host.hypervisor.cpu_utilization``,
and integrates the result over time into per-host energy figures (kWh)
at the end of a run. (``Energy`` reports kWh, so it assumes one
simulation time unit is one second - see :mod:`skya.core.clock`.)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

# Imported only for type hints. A plain ``from skya.models import PM``
# would be a circular import - ``skya.models`` imports this module to
# give every ``PM`` a default power model. ``TYPE_CHECKING`` is ``True``
# for type checkers and IDEs, ``False`` at runtime, so this import is
# skipped when the program actually runs.
if TYPE_CHECKING:
    from skya.models import PM


class PowerModel(ABC):
    """Predicts a host's instantaneous power draw, in watts.

    Attached per :class:`PM` and queried by the :class:`skya.metrics.Energy`
    tracker on every :data:`Topic.SIM_TICK`. Override :meth:`power` for
    non-linear curves (cubic, table-driven, DVFS, …) - most subclasses
    are one method. ``host`` is passed in case the curve depends on the
    hardware (CPU generation, core count); :class:`LinearPower` ignores it.
    """

    @abstractmethod
    def power(self, host: PM, utilization: float) -> float:
        """Return power draw in watts for ``host`` at CPU ``utilization``
        (a fraction in ``[0, 1]``)."""


@dataclass
class LinearPower(PowerModel):
    """Linear interpolation between idle and peak power.

    The classic SPECpower-style model: ``P(u) = idle + (peak - idle) · u``,
    where ``u`` is the host's CPU utilization in ``[0, 1]``. Any memory
    contribution is absorbed into the linear term - researchers needing
    more granularity subclass with the same signature.
    """

    idle: float
    """Watts drawn when the host is idle (``u = 0``) - including when it
    is powered on but hosts no VMs."""

    peak: float
    """Watts drawn when the host's CPU is fully utilized (``u = 1``)."""

    def power(self, host: PM, utilization: float) -> float:
        u: float = max(0.0, min(1.0, utilization))
        return self.idle + (self.peak - self.idle) * u


@dataclass
class ZeroPower(PowerModel):
    """A power model that always reports zero. The default for hosts
    whose energy draw is not modeled, so the :class:`Energy` tracker
    can still run, reporting zero for those hosts."""

    def power(self, host: PM, utilization: float) -> float:
        return 0.0
