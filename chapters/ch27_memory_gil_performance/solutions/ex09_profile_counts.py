"""
Exercise 09 — Profile Without Timings: Call Counts and Allocation Sites  [Tier: ◆ Extended]
Chapter 27 · Pattern: cProfile ncalls + tracemalloc snapshots · Target time: 25 min

Problem
-------
Timings are noisy, but some profiler facts are exact and repeatable.

1. `call_counts(func, *args)` profiles one call with cProfile and returns
   {function_name: ncalls} for Python functions defined in THIS file
   (skip built-ins, `<lambda>`, `<genexpr>`, comprehensions). For a
   recursive function count every call, not just the outermost ones.
2. `top_allocation_line(func, *args)` takes a tracemalloc snapshot while
   the result of `func(*args)` is still alive and returns the stripped
   source text of the line in THIS file that holds the most allocated bytes.

Demo: naive `fib(20)` versus `lru_cache` `fib_memo(20)`; and a `build_report`
pipeline whose biggest allocation is the padded-row list.

Examples
--------
>>> call_counts(fib, 10)
{'fib': 177}
>>> call_counts(fib_memo_fresh, 10)
{'fib_memo': 11}

Constraints
-----------
- Output must not contain timings, so it is identical on every run.

Approach ladder
---------------
1. Brute force — sprinkle counters and `print` calls into the code.
2. Improved   — cProfile sorted by `tottime` to find the hotspot (→ §22.8);
   the right tool, but the times change run to run.
3. Optimal    — use the deterministic parts: `ncalls` proves an exponential
   call tree (fib(n) makes 2*F(n+1) - 1 calls) and that memoisation makes it
   linear (n + 1 calls); tracemalloc groups live allocations by source line.
   Profiling adds overhead per call (cProfile) or per allocation
   (tracemalloc), so measure, then turn it off.

Hints
-----
- `pstats.Stats(profiler).stats` maps (file, line, name) -> (cc, nc, tt, ct,
  callers); `nc` counts recursive calls, `cc` only primitive ones.
- `snapshot.statistics("lineno")` sorts by size; filter on `__file__` with
  `tracemalloc.Filter(True, __file__)`.

Follow-ups
----------
- Why does a second `fib_memo(20)` show no Python calls at all? (The C-level
  lru_cache wrapper answers from the cache before the body runs; clear it
  with `fib_memo.cache_clear()` to measure again.)
- Sampling profilers (e.g. py-spy) have far lower overhead than cProfile's
  per-call hooks: use them on production processes.
"""
from __future__ import annotations

import cProfile
import linecache
import os
import pstats
import tracemalloc
from functools import lru_cache
from typing import Callable

THIS_FILE = os.path.abspath(__file__)


def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)


@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)


def fib_memo_fresh(n: int) -> int:
    fib_memo.cache_clear()
    return fib_memo(n)


def call_counts(func: Callable, *args) -> dict[str, int]:
    profiler = cProfile.Profile()
    profiler.runcall(func, *args)
    counts: dict[str, int] = {}
    for (file, _, name), (_, nc, _, _, _) in pstats.Stats(profiler).stats.items():
        if os.path.abspath(file) == THIS_FILE and not name.startswith("<"):
            counts[name] = counts.get(name, 0) + nc
    if func.__name__.endswith("_fresh"):          # hide the cache-clearing wrapper
        counts.pop(func.__name__, None)
    return dict(sorted(counts.items()))


def load(n: int) -> list[int]:
    return list(range(n))


def pad_rows(values: list[int]) -> list[str]:
    return [f"{v:>40}" for v in values]


def build_report(n: int) -> tuple[list[int], list[str]]:
    values = load(n)
    rows = pad_rows(values)
    return values, rows


def top_allocation_line(func: Callable, *args) -> str:
    tracemalloc.start()
    try:
        result = func(*args)                       # keep it alive for the snapshot
        snapshot = tracemalloc.take_snapshot().filter_traces(
            [tracemalloc.Filter(True, THIS_FILE)])
    finally:
        tracemalloc.stop()
    del result
    frame = snapshot.statistics("lineno")[0].traceback[0]
    return linecache.getline(frame.filename, frame.lineno).strip()


def main() -> None:
    for n in [10, 20]:
        print(f"fib({n}) calls:", call_counts(fib, n))
        print(f"fib_memo({n}) calls:", call_counts(fib_memo_fresh, n))
    print("build_report calls:", call_counts(build_report, 1000))
    print("top allocation line:", top_allocation_line(build_report, 20_000))


if __name__ == "__main__":
    main()
