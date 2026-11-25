"""
Exercise 05 — See the GIL: CPU-bound vs I/O-bound Threads    [Tier: ★ Core]
Chapter 27 · Pattern: boolean benchmark of a hypothesis · Target time: 20 min

Problem
-------
In the default (GIL) build of CPython, only one thread executes Python
bytecode at a time; a thread releases the GIL when it blocks on I/O or sleep,
and the interpreter asks the running thread to drop it every switch interval
(`sys.getswitchinterval()`, 0.005 s by default).

1. `gil_enabled()` returns True when the running interpreter has an active
   GIL. Use `sys._is_gil_enabled()` where it exists (3.13+); older versions
   always have a GIL.
2. `speedup(task, workers)` runs `task()` `workers` times sequentially, then
   once per thread concurrently, and returns sequential_time / threaded_time
   (best of 3 for each).
3. `report()` returns a dict of booleans:
     "gil enabled"                         gil_enabled()
     "threads overlap sleep-bound work"    speedup(sleepy, 4) > 2
     "threads speed up CPU-bound work"     speedup(spin, 4) > 1.5
     "CPU result matches the build"        the previous line == (not gil_enabled())

Examples
--------
>>> report()["threads overlap sleep-bound work"]
True

Constraints
-----------
- Print booleans only; the whole run stays under a few seconds.


Hints
-----
- `time.sleep` releases the GIL; a pure-Python loop holds it except at
  switch-interval hand-offs.
- `threading.Thread(target=task)` then `start()` all, then `join()` all.

Follow-ups
----------
- Why can CPU-bound threads be *slower* than sequential? (GIL hand-offs and
  cache effects add overhead without adding parallelism.)
- What changes with NumPy or hashlib on large buffers? (Their C code
  releases the GIL, so threads can run in parallel.)
"""
from __future__ import annotations

import sys
import threading
import time
from typing import Callable


def gil_enabled() -> bool:
    raise NotImplementedError("TODO")


def spin(n: int = 300_000) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total


def sleepy(seconds: float = 0.05) -> None:
    time.sleep(seconds)


def _best(fn: Callable[[], None], repeats: int = 3) -> float:
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def speedup(task: Callable[[], object], workers: int) -> float:
    raise NotImplementedError("TODO")


def report() -> dict[str, bool]:
    raise NotImplementedError("TODO")


def main() -> None:
    print("default switch interval is 5 ms:", sys.getswitchinterval() == 0.005)
    for claim, ok in report().items():
        print(f"{claim}: {ok}")


if __name__ == "__main__":
    main()
