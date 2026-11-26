"""
Exercise 10 — Statistics From an Exhausted Iterator     [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (iteration) · Target time: 8 min

Problem
-------
`summary(values)` receives ANY iterable of numbers — a list, a generator
expression, a `map` object — and must return `(minimum, maximum, mean)`. The
buggy version calls `min(values)`, then `max(values)`, then `sum(values)`. With a
generator or `map`, the first call consumes everything, so `max` sees an empty
iterator and raises `ValueError`.

Examples
--------
>>> summary([3, 1, 2])
(1, 3, 2.0)
>>> summary(x * x for x in range(4))
(0, 9, 3.5)

Constraints
-----------
- At least one value (an empty input should raise ValueError with a clear message).

Approach ladder
---------------
1. Buggy  — assumes it can iterate multiple times.
2. Fixed  — materialise once: `values = list(values)`. O(n) extra space.
3. One pass — track min, max, sum and count in a single loop: O(1) extra space,
   works on streams too large to hold in memory (it still needs them to end).

Follow-ups
----------
- Which built-ins return single-use iterators? (`zip`, `map`, `filter`,
  `reversed`, `enumerate`, `iter`, generator expressions, file objects.)
- How do you peek at an iterator without losing the item? (`itertools.tee`, or
  re-chain: `itertools.chain([first], it)`.)
"""
from __future__ import annotations

from typing import Iterable


def buggy_summary(values: Iterable[float]) -> tuple[float, float, float]:
    lo = min(values)
    hi = max(values)          # ValueError if `values` was a one-shot iterator
    mean = sum(values) / len(list(values))
    return lo, hi, mean


def summary(values: Iterable[float]) -> tuple[float, float, float]:
    """Single pass over any iterable: O(n) time, O(1) extra space."""
    count = 0
    total = 0
    lo = hi = None
    for v in values:
        if count == 0:
            lo = hi = v
        else:
            lo = min(lo, v)
            hi = max(hi, v)
        total += v
        count += 1
    if count == 0:
        raise ValueError("summary() needs at least one value")
    return lo, hi, total / count


def main() -> None:
    print("buggy on a list:", buggy_summary([3, 1, 2]))
    try:
        buggy_summary(x * x for x in range(4))
    except ValueError as exc:
        print("buggy on a generator:", type(exc).__name__, "-", exc)
    print("fixed on a list:", summary([3, 1, 2]))
    print("fixed on a generator:", summary(x * x for x in range(4)))
    print("fixed on map:", summary(map(int, ["5", "7"])))
    z = zip("ab", [1, 2])
    print("zip first pass:", list(z), "| second pass:", list(z))


if __name__ == "__main__":
    main()
