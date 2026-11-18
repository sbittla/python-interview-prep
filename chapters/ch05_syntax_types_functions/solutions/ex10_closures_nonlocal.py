"""
Exercise 10 — Counters and Running Averages With Closures     [Tier: ★ Core]
Chapter 05 · Pattern: LEGB scope, nonlocal · Target time: 15 min

Problem
-------
Implement two closure factories:

- ``solve(start=0, step=1)`` returns a pair of functions ``(increment, current)``.
  ``increment()`` advances the counter by ``step`` and returns the new value; ``current()``
  returns the value without changing it. Counters created by separate calls are independent.
- ``make_averager()`` returns a function ``add(x)`` that records x and returns the running
  mean of every value seen so far, storing only a total and a count (O(1) memory).

Examples
--------
>>> inc, cur = solve(10, 5)
>>> inc(), inc(), cur()
(15, 20, 20)
>>> avg = make_averager(); avg(10), avg(20), avg(60)
(10.0, 15.0, 30.0)

Constraints
-----------
- no global variables and no classes: state must live in the enclosing function's scope

Approach ladder
---------------
1. Brute force — keep the state in a module-level global and use ``global``. Works for one
   counter, but two counters share the same global, and tests interfere with each other.
2. Optimal    — keep the state in the enclosing function and rebind it from the inner
   function with ``nonlocal``. Every factory call creates a fresh scope, so counters are
   independent. O(1) time and space per call. Without ``nonlocal``, ``count += 1`` raises
   UnboundLocalError because assignment makes ``count`` local to the inner function.

Follow-ups
----------
- Mutating a container (``state["n"] += 1``) works without ``nonlocal``. Why? You never rebind
  the name, you only mutate the object it refers to.
- When would you switch to a class? When you need several methods, inspection or pickling.
"""
from __future__ import annotations

from collections.abc import Callable

_global_count = 0


def brute_force_increment() -> int:
    global _global_count
    _global_count += 1
    return _global_count


def solve(start: int = 0, step: int = 1) -> tuple[Callable[[], int], Callable[[], int]]:
    value = start

    def increment() -> int:
        nonlocal value
        value += step
        return value

    def current() -> int:
        return value            # reading an enclosing name needs no declaration

    return increment, current


def make_averager() -> Callable[[float], float]:
    total = 0.0
    count = 0

    def add(x: float) -> float:
        nonlocal total, count
        total += x
        count += 1
        return total / count

    return add


def main() -> None:
    inc_a, cur_a = solve()
    inc_b, cur_b = solve(100, 10)
    print("a:", inc_a(), inc_a(), inc_a(), "| b:", inc_b(), inc_b(), "| a now", cur_a(), "b now", cur_b())
    avg = make_averager()
    print("running means:", [avg(x) for x in (10, 20, 60, 10)])
    print("closure cells:", [c.cell_contents for c in inc_b.__closure__])

    def broken():
        count = 0

        def bump():
            count += 1          # assignment makes `count` local to bump
            return count
        return bump

    try:
        broken()()
    except UnboundLocalError as exc:
        print("UnboundLocalError:", exc)
    print("global version:", brute_force_increment(), brute_force_increment())


if __name__ == "__main__":
    main()
