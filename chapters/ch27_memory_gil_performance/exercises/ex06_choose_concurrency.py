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
    raise NotImplementedError("TODO")


def overlap_demo(n: int, delay: float) -> dict[str, bool]:
    raise NotImplementedError("TODO")


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
