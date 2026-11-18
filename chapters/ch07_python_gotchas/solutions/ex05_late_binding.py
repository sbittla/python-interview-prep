"""
Exercise 05 — Late-Binding Lambdas and a Broken Counter [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (scope) · Target time: 8 min

Problem
-------
1. `make_multipliers(n)` must return n functions where the i-th function
   multiplies its argument by i. The buggy version builds lambdas in a loop; all
   of them look up `i` when CALLED, by which time the loop has finished.
2. `make_counter()` must return a function that returns 1, 2, 3, ... on
   successive calls. The buggy version does `count += 1` inside the inner
   function without `nonlocal`, which raises UnboundLocalError.

Examples
--------
>>> [f(10) for f in make_multipliers(3)]
[0, 10, 20]
>>> c = make_counter(); c(), c(), c()
(1, 2, 3)

Constraints
-----------
- 0 <= n <= 1000

Approach ladder
---------------
1. Buggy  — closures capture VARIABLES, not values; assignment inside a function
   makes a name local to that function for the whole body.
2. Fixed  — bind the current value with a default argument (`lambda x, i=i: x * i`)
   or `functools.partial`; declare `nonlocal count` in the counter.

Follow-ups
----------
- Does a list comprehension fix late binding? (No — the comprehension has its
  own scope, but every lambda still sees the final `i`.)
- `global` vs `nonlocal`: which scope does each rebind?
"""
from __future__ import annotations

from typing import Callable


def buggy_make_multipliers(n: int) -> list[Callable[[int], int]]:
    return [lambda x: x * i for i in range(n)]


def buggy_make_counter() -> Callable[[], int]:
    count = 0

    def step() -> int:
        count += 1  # noqa: F823  -- UnboundLocalError: assignment makes `count` local
        return count

    return step


def make_multipliers(n: int) -> list[Callable[[int], int]]:
    """i-th function multiplies by i; the default argument freezes i's value."""
    return [lambda x, i=i: x * i for i in range(n)]


def make_counter() -> Callable[[], int]:
    count = 0

    def step() -> int:
        nonlocal count
        count += 1
        return count

    return step


def main() -> None:
    print("buggy multipliers:", [f(10) for f in buggy_make_multipliers(3)])
    print("fixed multipliers:", [f(10) for f in make_multipliers(3)])
    try:
        buggy_make_counter()()
    except UnboundLocalError as exc:
        print("buggy counter:", type(exc).__name__)
    c = make_counter()
    print("fixed counter:", [c() for _ in range(3)])


if __name__ == "__main__":
    main()
