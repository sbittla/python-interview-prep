"""
Exercise 06 — Processes, Threads or asyncio?                 [Tier: ★ Core]
Chapter 27 · Pattern: workload classification · Target time: 15 min

Problem
-------
1. `choose(workload)` takes a dict of booleans describing a job and returns
   one of "sequential", "processes", "threads", "asyncio":
     "parallel_worth_it"  False -> "sequential" (tiny job, or one task)
     "cpu_bound"          True  -> "processes", unless "gil_free" is True
                                   (free-threaded build or C code that
                                   releases the GIL) -> "threads"
     otherwise (I/O-bound):
       "many_connections" True (thousands of sockets) and
       "async_libraries"  True                       -> "asyncio"
       else                                          -> "threads"
   Missing keys count as False.
2. `overlap_demo(n, delay)` runs n waits of `delay` seconds three ways
   (sequential sleeps, a ThreadPoolExecutor, asyncio.gather of
   asyncio.sleep) and returns {"threads overlap": bool, "asyncio overlaps":
   bool}: True when that variant took less than half the sequential time.

Examples
--------
>>> choose({"parallel_worth_it": True, "cpu_bound": True})
'processes'
>>> choose({"parallel_worth_it": True, "many_connections": True, "async_libraries": True})
'asyncio'

Constraints
-----------
- `overlap_demo(20, 0.02)` finishes well under a second of waiting.

Approach ladder
---------------
1. Brute force — "use threads for everything". Fails for CPU-bound pure
   Python on the default build: the GIL serialises bytecode.
2. Improved   — CPU -> processes, I/O -> threads. Right, but every OS thread
   reserves its own stack (platform-dependent virtual memory) and costs a
   kernel context switch; ten thousand idle sockets want an event loop.
3. Optimal    — decide on (CPU vs I/O) x (GIL vs GIL-free) x (how many waits,
   are async libraries available), and say the trade-off aloud. Processes
   pay pickling and start-up costs; asyncio needs every blocking call to be
   awaitable (or pushed to a thread, → §28.9). O(1) per decision.

Hints
-----
- `concurrent.futures.ThreadPoolExecutor(max_workers=n).map(fn, items)`.
- `asyncio.run(main())` with `await asyncio.gather(*coros)`.

Follow-ups
----------
- Mixed job: parse CPU-heavy files fetched over HTTP? (asyncio or threads
  for fetching, a process pool for parsing.)
- When is "sequential" the senior answer? (When the job takes milliseconds:
  pool start-up and pickling cost more than they save.)
"""
from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor


def choose(workload: dict[str, bool]) -> str:
    w = lambda key: bool(workload.get(key, False))     # noqa: E731
    if not w("parallel_worth_it"):
        return "sequential"
    if w("cpu_bound"):
        return "threads" if w("gil_free") else "processes"
    if w("many_connections") and w("async_libraries"):
        return "asyncio"
    return "threads"


def overlap_demo(n: int, delay: float) -> dict[str, bool]:
    start = time.perf_counter()
    for _ in range(n):
        time.sleep(delay)
    sequential = time.perf_counter() - start

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n) as pool:
        list(pool.map(time.sleep, [delay] * n))
    threaded = time.perf_counter() - start

    async def waits() -> None:
        await asyncio.gather(*(asyncio.sleep(delay) for _ in range(n)))

    start = time.perf_counter()
    asyncio.run(waits())
    async_time = time.perf_counter() - start

    return {"threads overlap": threaded < sequential / 2,
            "asyncio overlaps": async_time < sequential / 2}


def main() -> None:
    jobs = {
        "resize 10k images (pure Python)": {"parallel_worth_it": True, "cpu_bound": True},
        "same, free-threaded build": {"parallel_worth_it": True, "cpu_bound": True, "gil_free": True},
        "call 20 REST APIs": {"parallel_worth_it": True},
        "10k websocket clients": {"parallel_worth_it": True, "many_connections": True,
                                  "async_libraries": True},
        "10k sockets, blocking-only SDK": {"parallel_worth_it": True, "many_connections": True},
        "sum a 1,000-item list": {"cpu_bound": True},
    }
    for name, job in jobs.items():
        print(f"{name:32} -> {choose(job)}")
    for claim, ok in overlap_demo(20, 0.02).items():
        print(f"{claim}: {ok}")


if __name__ == "__main__":
    main()
