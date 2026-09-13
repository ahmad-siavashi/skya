"""``skya.core`` - the discrete-event engine that drives a simulation.

Internal infrastructure: researchers extending Skya (a custom
placement, scheduler, hypervisor, tracker, power model, …) do not need
to read any of this. It holds the time source (:class:`Clock`), the
publish/subscribe event queue (:class:`EventQueue`, plus the :func:`on`
handler decorator), and the mixin the pluggable policies share - create
the object on its own, then bind it to its owner (:class:`Bound`).

The user-facing pieces are re-exported from the package root -
``from skya import on, EventQueue, Clock`` - so most code never imports
``skya.core`` directly; everything else stays here.
"""

from __future__ import annotations

from skya.core.binding import Bound
from skya.core.clock import Clock, Time
from skya.core.event_queue import EventQueue, on

__all__ = ['Bound', 'Clock', 'EventQueue', 'Time', 'on']
