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

Approach ladder
---------------
1. Brute force — call the blocking function in the coroutine: the whole loop (every task,
   every timeout) stops for its duration. Works only for calls of microseconds.
2. Improved   — `await asyncio.to_thread(f, *args)`: the call runs in the loop's default
   thread pool; the loop keeps serving tasks. Fine for blocking I/O (it releases the GIL).
3. Optimal for CPU-bound work — threads still share one GIL in the default build (→ §27.5),
   so pure-Python CPU work in `to_thread` slows other threads; use
   `loop.run_in_executor(process_pool, f, *args)` (arguments and results are pickled).
   Best of all: an async-native library (aiohttp, asyncpg) so no thread is needed.

Hints
-----
- `asyncio.to_thread` copies the current `contextvars` context into the thread.
- A sync function in an `async def` is still sync; adding `async` does not make it non-blocking.
- Spot the bug in reviews: `time.sleep` inside a coroutine (use `await asyncio.sleep`).

Follow-ups
----------
- Default executor size: `min(32, os.cpu_count() + 4)` threads; pass your own executor for
  more control.
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
    ticks: list[int] = []
    ready = threading.Event()
    hb = asyncio.create_task(heartbeat(ticks, ready))
    saw = legacy_read(ready, 0.2)       # loop frozen: heartbeat never gets a turn
    during = len(ticks)
    await hb
    return saw, during


async def call_to_thread() -> tuple[bool, int]:
    ticks: list[int] = []
    ready = threading.Event()
    hb = asyncio.create_task(heartbeat(ticks, ready))
    saw = await asyncio.to_thread(legacy_read, ready, 5.0)   # loop keeps running
    during = len(ticks)
    await hb
    return saw, during


async def call_run_in_executor() -> tuple[bool, int]:
    ticks: list[int] = []
    ready = threading.Event()
    hb = asyncio.create_task(heartbeat(ticks, ready))
    loop = asyncio.get_running_loop()
    saw = await loop.run_in_executor(None, legacy_read, ready, 5.0)
    during = len(ticks)
    await hb
    return saw, during


async def cpu_in_process(n: int) -> int:
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=1) as pool:
        return await loop.run_in_executor(pool, sum_squares, n)


def main() -> None:
    print("direct blocking call (saw event, ticks during):", asyncio.run(call_blocking()))
    print("asyncio.to_thread                              :", asyncio.run(call_to_thread()))
    print("loop.run_in_executor(None, ...)                :",
          asyncio.run(call_run_in_executor()))
    print("CPU work in a process pool:", asyncio.run(cpu_in_process(10**6)) == sum_squares(10**6))


if __name__ == "__main__":
    main()
