"""
Exercise 06 — Timing and Logging Decorators (injectable clock)          [Tier: ★ Core]
Chapter 25 · Pattern: cross-cutting concern as a decorator · Target time: 20 min

Problem
-------
1. `timed(clock=time.perf_counter, report=print)` — a decorator factory. Each call
   reads `clock()` before and after, stores the difference on the wrapper as
   `last_elapsed`, and calls `report(f"{name} took {elapsed:.3f}s")`. Timing is
   reported even when the function raises (the exception still propagates).
2. `log_calls(log)` — a decorator factory that calls `log` with
   "call add(2, b=3)" before and "add -> 5" after, or "add raised
   ValueError('boom')" and re-raises. Arguments are shown with repr().
3. `FakeClock(step)` — a test clock: each call returns the previous value + step,
   starting at 0.0. With it, timings are exact and no real time passes.

Examples
--------
>>> lines = []
>>> add = log_calls(lines.append)(lambda a, b: a + b)
>>> add(2, b=3), lines
(5, ['call <lambda>(2, b=3)', '<lambda> -> 5'])

Constraints
-----------
- Decorators must not change return values or swallow exceptions.

Approach ladder
---------------
1. Brute force — `start = time.perf_counter()` / print at every call site:
   duplicated, untestable output that changes on every run.
2. Decorator with hard-coded clock and print — reusable but non-deterministic.
3. Optimal — inject `clock` and `report`/`log` (any callable): O(1) overhead per
   call (plus O(size of args) to format the log line). Tests pass a FakeClock
   and list.append, so output is exact. Use try/finally so a failing call is
   still timed. Why move up: production behaviour unchanged, tests deterministic.

Hints
-----
- `time.perf_counter()` is the clock meant for durations (high resolution, not
  adjustable); `time.time()` is wall-clock time and can jump when it is set.
- `", ".join([*map(repr, args), *(f"{k}={v!r}" for k, v in kwargs.items())])`.
- In production pass `logging.getLogger(__name__).info` as `log` (logging is §26.8).

Follow-ups
----------
- Aggregate: total time and call count per function in a dict.
- Make `timed` work both as `@timed` and `@timed(clock=...)` (see ex04's tag).
- Why can a timing decorator mislead for recursive functions? (each level is timed)
"""
from __future__ import annotations

import time
from functools import wraps
from typing import Callable


class FakeClock:
    def __init__(self, step: float) -> None:
        self.step, self.now = step, -step

    def __call__(self) -> float:
        self.now += self.step
        return self.now


def timed(clock: Callable[[], float] = time.perf_counter,
          report: Callable[[str], object] = print):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = clock()
            try:
                return func(*args, **kwargs)
            finally:
                wrapper.last_elapsed = clock() - start
                report(f"{func.__name__} took {wrapper.last_elapsed:.3f}s")
        wrapper.last_elapsed = None
        return wrapper
    return decorator


def _format_call(name: str, args: tuple, kwargs: dict) -> str:
    parts = [*map(repr, args), *(f"{k}={v!r}" for k, v in kwargs.items())]
    return f"{name}({', '.join(parts)})"


def log_calls(log: Callable[[str], object]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log("call " + _format_call(func.__name__, args, kwargs))
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                log(f"{func.__name__} raised {exc!r}")
                raise
            log(f"{func.__name__} -> {result!r}")
            return result
        return wrapper
    return decorator


def main() -> None:
    lines: list[str] = []

    @timed(clock=FakeClock(0.25), report=lines.append)
    @log_calls(lines.append)
    def divide(a: float, b: float = 1.0) -> float:
        return a / b

    divide(9, b=2)
    try:
        divide(1, 0)
    except ZeroDivisionError:
        lines.append("caller saw ZeroDivisionError")
    print("\n".join(lines))
    print("last_elapsed:", divide.last_elapsed, "| name:", divide.__name__)
    real = timed(report=lambda msg: None)(sum)
    real(range(1000))
    print("real clock gives a float >= 0:", real.last_elapsed >= 0.0)


if __name__ == "__main__":
    main()
