"""Virtual-time asyncio runner used by every Chapter 42 exercise.

Real ``asyncio`` code (``asyncio.sleep``, ``wait_for``, ``Semaphore``, ``gather``...) runs unchanged,
but the event loop's clock is *simulated*: whenever the loop would block waiting for the next timer,
the clock jumps straight to that timer instead of sleeping. Consequences:

* a "2 second" LLM call finishes instantly in wall-clock time;
* ``loop.time()`` (read via :func:`now`) returns exact, reproducible simulated seconds;
* output is deterministic, so it can be printed and compared byte-for-byte.

This is the same idea as the "virtual clock" helpers in test libraries; it is a teaching tool,
not something you deploy. Python 3.10+ compatible.
"""
from __future__ import annotations

import asyncio
from typing import Any, Awaitable


class _VirtualSelector:
    """Wraps the real selector: polls without blocking, then advances virtual time."""

    def __init__(self, loop: "VirtualTimeLoop", real: Any) -> None:
        self._loop = loop
        self._real = real

    def select(self, timeout: float | None = None):
        events = self._real.select(0)  # never block in wall-clock time
        if events:
            return events
        if timeout is None:
            raise RuntimeError("virtual loop deadlock: nothing is scheduled and nothing is ready")
        if timeout > 0:
            self._loop._virtual_now += timeout  # jump to the next timer
        return events

    def __getattr__(self, name: str) -> Any:  # register/unregister/close/get_map ...
        return getattr(self._real, name)


class VirtualTimeLoop(asyncio.SelectorEventLoop):
    def __init__(self) -> None:
        super().__init__()
        self._virtual_now = 0.0
        self._selector = _VirtualSelector(self, self._selector)

    def time(self) -> float:  # used by sleep, wait_for, call_later, timeouts
        return self._virtual_now


def run(coro: Awaitable[Any]) -> Any:
    """Like ``asyncio.run`` but on a fresh virtual-time loop starting at t=0."""
    loop = VirtualTimeLoop()
    try:
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.run_until_complete(loop.shutdown_asyncgens())
        return result
    finally:
        asyncio.set_event_loop(None)
        loop.close()


def now() -> float:
    """Current simulated time (seconds, rounded to avoid float noise)."""
    return round(asyncio.get_running_loop().time(), 6)
