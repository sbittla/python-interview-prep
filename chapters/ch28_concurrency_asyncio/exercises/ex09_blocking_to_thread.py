"""
Exercise 09 — A Blocking Call Freezes the Loop; to_thread Fixes It   [Tier: ◆ Extended]
Chapter 28 · Pattern: asyncio.to_thread / run_in_executor · Target time: 20 min

Problem
-------
`legacy_read(ready, timeout)` is a given *blocking* function (think `requests.get` or a
database driver): it waits up to `timeout` seconds on a `threading.Event` and returns whether
the event was set. A heartbeat coroutine ticks every 10 ms and sets that event on its 3rd tick.

1. `call_blocking()` — start the heartbeat task, then call `legacy_read` *directly* inside the
   coroutine. Return `(read_saw_event, ticks_during_call)`.
2. `call_to_thread()` — the same, but `await asyncio.to_thread(legacy_read, ...)` (3.9+).
3. `call_run_in_executor()` — the same via `loop.run_in_executor(None, ...)` (any 3.x).
4. `cpu_in_process(n)` — offload the CPU-bound `sum_squares(n)` to a `ProcessPoolExecutor`
   with `run_in_executor` and return its result.

Examples
--------
>>> asyncio.run(call_blocking())
(False, 0)
>>> asyncio.run(call_to_thread())
(True, 3)

Constraints
-----------
- The outputs must not depend on timing: the direct call returns False because the heartbeat
  *cannot* run while the loop is blocked, not because it was slow.


Hints
-----
- `asyncio.to_thread` copies the current `contextvars` context into the thread.
- A sync function in an `async def` is still sync; adding `async` does not make it non-blocking.
- Spot the bug in reviews: `time.sleep` inside a coroutine (use `await asyncio.sleep`).

Follow-ups
----------
- Default executor: a `ThreadPoolExecutor` of up to `min(32, cpus + 4)` threads, where cpus is
  `os.cpu_count()` before 3.13 and `os.process_cpu_count()` from 3.13; pass your own
  executor for more control.
- Debug mode (`PYTHONASYNCIODEBUG=1` or `asyncio.run(..., debug=True)`) logs callbacks slower
  than 100 ms.
"""
from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ProcessPoolExecutor


def legacy_read(ready: threading.Event, timeout: float) -> bool:  # given
    return ready.wait(timeout)          # blocks the calling thread


def sum_squares(n: int) -> int:  # given
    return sum(i * i for i in range(n))


async def heartbeat(ticks: list[int], ready: threading.Event) -> None:  # given
    for i in range(1, 4):
        await asyncio.sleep(0.01)
        ticks.append(i)
    ready.set()


async def call_blocking() -> tuple[bool, int]:
    raise NotImplementedError("TODO")


async def call_to_thread() -> tuple[bool, int]:
    raise NotImplementedError("TODO")


async def call_run_in_executor() -> tuple[bool, int]:
    raise NotImplementedError("TODO")


async def cpu_in_process(n: int) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    print("direct blocking call (saw event, ticks during):", asyncio.run(call_blocking()))
    print("asyncio.to_thread                              :", asyncio.run(call_to_thread()))
    print("loop.run_in_executor(None, ...)                :",
          asyncio.run(call_run_in_executor()))
    print("CPU work in a process pool:", asyncio.run(cpu_in_process(10**6)) == sum_squares(10**6))


if __name__ == "__main__":
    main()
