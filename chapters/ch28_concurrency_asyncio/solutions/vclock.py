"""Virtual-time asyncio runner shared by the chapter's async exercises (helper, not an exercise).

`run_virtual(coro)` runs a coroutine on an event loop whose clock is *virtual*: whenever every
task is asleep, the loop jumps straight to the next timer instead of waiting. `asyncio.sleep`,
`wait_for`, `asyncio.timeout` and `loop.time()` all see the virtual clock, so a demo that
"sleeps" 10 s finishes instantly and prints the same timings on every run.

How it works: the loop's selector is asked to wait `timeout` seconds only when no callback is
ready; we advance the clock by `timeout` and poll without blocking. A `None` timeout (nothing
scheduled, waiting on real I/O or a thread) still blocks for real.

Restrictions: do not mix with threads (`to_thread`) or real I/O; virtual time would race them.
Works on Python 3.10+ (uses only public `SelectorEventLoop(selector)` and `loop.time()`).
"""
from __future__ import annotations

import asyncio
import selectors
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")


class _VirtualSelector(selectors.DefaultSelector):
    def __init__(self) -> None:
        super().__init__()
        self.now = 0.0

    def select(self, timeout: float | None = None):
        if timeout is not None and timeout > 0:
            self.now += timeout                  # jump to the next timer instead of sleeping
            timeout = 0
        return super().select(timeout)


class VirtualTimeLoop(asyncio.SelectorEventLoop):
    def __init__(self) -> None:
        self._vsel = _VirtualSelector()
        super().__init__(self._vsel)

    def time(self) -> float:
        return self._vsel.now


def run_virtual(coro: Coroutine[Any, Any, T]) -> T:
    """Like asyncio.run(coro), but on a fresh VirtualTimeLoop starting at t = 0."""
    loop = VirtualTimeLoop()
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
        finally:
            asyncio.set_event_loop(None)
            loop.close()
