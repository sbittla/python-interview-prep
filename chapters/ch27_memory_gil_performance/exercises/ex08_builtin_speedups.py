"""
Exercise 08 — Let C Do the Loop: Built-ins vs Hand-Written Loops  [Tier: ◆ Extended]
Chapter 27 · Pattern: rewrite + equivalence check + boolean race · Target time: 20 min

Problem
-------
Each slow function below is correct but runs its loop in Python bytecode.
Write the fast twin using built-ins, prove both agree on edge cases, and
race them.

  slow_total(xs)        manual accumulator        -> fast_total: sum()
  slow_largest(xs)      manual max, None if empty -> fast_largest: max(default=)
  slow_sorted(xs)       insertion sort, O(n^2)    -> fast_sorted: sorted()
  slow_common(a, b)     nested `in` on lists      -> fast_common: set intersection
                        (returns sorted unique common items)

`race(n)` returns {name: fast_is_faster} for each pair on the same input of
size n (best of 3 timings each; print only the booleans).

Examples
--------
>>> fast_common([3, 1, 3, 2], [2, 3, 5])
[2, 3]
>>> fast_largest([])            # None, like slow_largest

Constraints
-----------
- Items are ints. `race(2_000)` runs in well under a second.


Hints
-----
- `max(xs, default=None)` handles the empty case.
- `sorted(set(a) & set(b))` for unique common items in order.

Follow-ups
----------
- When does a comprehension beat `map(lambda ...)`? (A lambda call per item
  costs a Python frame; a comprehension does the work inline.)
- What do 3.11's speedups change here? (Interpreted loops got faster, so
  the ratio shrinks, but C built-ins still win by a wide margin.)
"""
from __future__ import annotations

import random
import time
from typing import Callable


def slow_total(xs: list[int]) -> int:
    total = 0
    for x in xs:
        total += x
    return total


def fast_total(xs: list[int]) -> int:
    raise NotImplementedError("TODO")


def slow_largest(xs: list[int]) -> int | None:
    best = None
    for x in xs:
        if best is None or x > best:
            best = x
    return best


def fast_largest(xs: list[int]) -> int | None:
    raise NotImplementedError("TODO")


def slow_sorted(xs: list[int]) -> list[int]:
    out = list(xs)
    for i in range(1, len(out)):
        key, j = out[i], i - 1
        while j >= 0 and out[j] > key:
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = key
    return out


def fast_sorted(xs: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def slow_common(a: list[int], b: list[int]) -> list[int]:
    found: list[int] = []
    for x in a:
        if x in b and x not in found:
            found.append(x)
    return sorted(found)


def fast_common(a: list[int], b: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


PAIRS: dict[str, tuple[Callable, Callable]] = {
    "total": (slow_total, fast_total),
    "largest": (slow_largest, fast_largest),
    "sorted": (slow_sorted, fast_sorted),
    "common": (slow_common, fast_common),
}


def _best(fn: Callable[[], object], repeats: int = 3) -> float:
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def race(n: int) -> dict[str, bool]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [[], [7], [3, -1, 3, 0], [5, 4, 3, 2, 1]]
    for name, (slow, fast) in PAIRS.items():
        if name == "common":
            agree = all(slow(c, [3, 0, 9]) == fast(c, [3, 0, 9]) for c in cases)
        else:
            agree = all(slow(c) == fast(c) for c in cases)
        print(f"{name:8} slow and fast agree on edge cases: {agree}")
    print("fast_common([3, 1, 3, 2], [2, 3, 5]) =", fast_common([3, 1, 3, 2], [2, 3, 5]))
    for name, ok in race(2_000).items():
        print(f"{name:8} built-in is faster: {ok}")


if __name__ == "__main__":
    main()
