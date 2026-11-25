"""
Exercise 06 — Find the Hotspot with cProfile and timeit     [Tier: ◆ Extended]
Chapter 22 · Pattern: measure before optimising · Target time: 20 min

Problem
-------
``pipeline(n)`` parses n fake records, removes duplicates and summarises them.
One stage is accidentally O(n^2). Write:

- ``own_times(func, *args)`` — run ``func(*args)`` under ``cProfile`` and
  return ``{function name: own time}`` for named Python functions (compare
  these; never print them).
- ``hottest(func, *args)`` — run ``func(*args)`` under ``cProfile`` and return
  the name of the function with the largest *own* time (``tottime``), ignoring
  built-ins (file "~") and anonymous code (<genexpr>, <lambda>, <listcomp>).
  Return only the name: never print timings.
- ``is_faster(fast, slow, number, repeat)`` — use ``timeit.repeat`` on two
  zero-argument callables and return True when the best run of ``fast`` beats
  the best run of ``slow``. (Taking the minimum filters out noise from other
  processes; it is the standard way to read timeit results.)

Then fix the hotspot and show the fixed pipeline returns the same result.

Examples
--------
>>> hottest(pipeline, 3000)
'dedupe_slow'
>>> pipeline(3000) == pipeline_fixed(3000)
True

Constraints
-----------
- Stdlib only. Output must be deterministic: names and booleans, not seconds.

Hints
-----
- cProfile.Profile().runcall(func, *args), then pstats.Stats(profiler).stats
  maps (file, line, name) -> (cc, nc, tottime, cumtime, callers).
- Built-ins have file "~"; skip names starting with "<".
- timeit.repeat(callable, number=..., repeat=...) returns a list; compare minima.
- The fix is a one-word change of container type.

Follow-ups
----------
- Why can cProfile exaggerate the cost of many tiny function calls?
  (It adds a fixed overhead per call.)
- Counting operations (ex01–ex04) beats timing for proving complexity;
  profiling answers "where is the time going in *this* run?"
"""
from __future__ import annotations

import cProfile
import pstats
import timeit


def parse(n: int) -> list[tuple[str, int]]:
    return [(f"user{i % (n // 2 or 1)}", i % 7) for i in range(n)]


def dedupe_slow(records: list[tuple[str, int]]) -> list[tuple[str, int]]:
    seen: list[str] = []
    out = []
    for name, score in records:
        if name not in seen:            # O(len(seen)) scan -> O(n^2) overall
            seen.append(name)
            out.append((name, score))
    return out


def dedupe_fast(records: list[tuple[str, int]]) -> list[tuple[str, int]]:
    raise NotImplementedError("TODO")


def summarise(records: list[tuple[str, int]]) -> tuple[int, int]:
    return len(records), sum(score for _, score in records)


def pipeline(n: int) -> tuple[int, int]:
    return summarise(dedupe_slow(parse(n)))


def pipeline_fixed(n: int) -> tuple[int, int]:
    return summarise(dedupe_fast(parse(n)))


def own_times(func, *args) -> dict[str, float]:
    """Profile func(*args); map each named Python function to its own time."""
    raise NotImplementedError("TODO")


def hottest(func, *args) -> str:
    raise NotImplementedError("TODO")


def best_own_time(func, n: int, name: str, runs: int = 3) -> float:
    """Warm up once, then the minimum own time of `name` over `runs` profiles.

    One cold profile is noisy; the minimum of several warm runs is stable enough
    to compare against a wide margin (never printed).
    """
    func(n)
    return min(own_times(func, n)[name] for _ in range(runs))


def is_faster(fast, slow, number: int = 3, repeat: int = 5) -> bool:
    raise NotImplementedError("TODO")


def main() -> None:
    print(f"hottest function in pipeline(3000): {hottest(pipeline, 3000)}")
    fixed_profile = own_times(pipeline_fixed, 3000)
    print(f"dedupe_slow absent from fixed profile: {'dedupe_slow' not in fixed_profile}")
    slow_tt = best_own_time(pipeline, 12_000, "dedupe_slow")
    fast_tt = best_own_time(pipeline_fixed, 12_000, "dedupe_fast")
    print(f"dedupe_fast own time < 25% of dedupe_slow's (n=12000, best of 3): "
          f"{fast_tt < 0.25 * slow_tt}")
    print(f"same result after fix: {pipeline(3000) == pipeline_fixed(3000)}")
    print(f"result: {pipeline_fixed(3000)}")
    records = parse(3000)
    print(f"set dedupe faster than list dedupe: "
          f"{is_faster(lambda: dedupe_fast(records), lambda: dedupe_slow(records))}")
    print(f"edge case n=1: {pipeline_fixed(1)}  n=0: {pipeline_fixed(0)}")


if __name__ == "__main__":
    main()
