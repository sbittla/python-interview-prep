"""Virtual-time asyncio runner shared by the chapter's async exercises (helper, not an exercise).

`run_virtual(coro)` runs a coroutine on an event loop whose clock is *virtual*: whenever every
task is asleep, the loop jumps straight to the next timer instead of waiting. `asyncio.sleep`,
`wait_for`, `asyncio.timeout` and `loop.time()` all see the virtual clock, so a demo that
"sleeps" 10 s finishes instantly and prints the same timings on every run.

How it works (CPython implementation detail, tested on 3.12 and 3.13): `BaseEventLoop._run_once`
passes the delay until the next timer to `selector.select(timeout)`. Our selector adds that
delay to the clock and polls without blocking. Two private details are relied on:

- `_run_once` → `select(timeout)` contract above.
- `loop._clock_resolution` (private): asyncio fires every timer due within this resolution.
  On Windows before 3.13 it is `time.get_clock_info("monotonic").resolution` = 0.015625 s, so
  sleeps of 5 ms and 12 ms would wake at the same virtual instant. We set it to 1e-9.

Deadlock guard: with no threads or real I/O, `select(None)` (nothing ready, no timer pending)
means every task waits on something no one will ever set. Instead of blocking forever we wait
`stall_seconds` of real time for any event and then raise `RuntimeError("virtual-clock
deadlock ...")`, so a buggy exercise fails fast instead of hanging.

Restrictions: do not mix with threads (`to_thread`) or real I/O; virtual time would race them.
"""
from __future__ import annotations

import asyncio
import selectors
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")


class _VirtualSelector(selectors.DefaultSelector):
    def __init__(self, stall_seconds: float) -> None:
        super().__init__()
        self.now = 0.0
        self.stall_seconds = stall_seconds

    def select(self, timeout: float | None = None):
        if timeout is None:                      # no timer pending and nothing ready
            events = super().select(self.stall_seconds)
            if not events:
                raise RuntimeError("virtual-clock deadlock: every task is waiting and "
                                   "no timer is pending")
            return events
        if timeout > 0:
            self.now += timeout                  # jump to the next timer instead of sleeping
        return super().select(0)


class VirtualTimeLoop(asyncio.SelectorEventLoop):
    def __init__(self, stall_seconds: float = 2.0) -> None:
        self._vsel = _VirtualSelector(stall_seconds)
        super().__init__(self._vsel)
        self._clock_resolution = 1e-9            # private attr; see module docstring

    def time(self) -> float:
        return self._vsel.now


def run_virtual(coro: Coroutine[Any, Any, T], stall_seconds: float = 2.0) -> T:
    """Like asyncio.run(coro), but on a fresh VirtualTimeLoop starting at t = 0."""
    loop = VirtualTimeLoop(stall_seconds)
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        try:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.run_until_complete(loop.shutdown_asyncgens())
        except RuntimeError:
            pass                                 # cleanup after a deadlock: best effort
        finally:
            asyncio.set_event_loop(None)
            loop.close()
