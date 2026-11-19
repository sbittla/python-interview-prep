"""
Exercise 08 — Minimum removals for non-overlapping intervals     [Tier: ★ Core]
Chapter 17 · Pattern: sort by end, keep greedily · Target time: 20 min

Problem
-------
Given intervals [start, end] with start < end, return the fewest intervals to remove so the
rest are pairwise non-overlapping, and the sorted indices of one such set of removed
intervals. The convention is a parameter:
- closed=False (half-open [s, e)): touching intervals [1, 2], [2, 3] do NOT conflict;
- closed=True  (closed [s, e]):    touching intervals DO conflict (they share the point 2).
Chapter 20 (Ex 01) proves the greedy choice; here the focus is the convention switch and
returning the witness.

Examples
--------
>>> solve([[1, 2], [2, 3], [3, 4], [1, 3]])
(1, [3])
>>> solve([[1, 2], [2, 3], [3, 4], [1, 3]], closed=True)
(2, [1, 3])
>>> solve([[1, 2], [1, 2], [1, 2]])
(2, [1, 2])

Constraints
-----------
- 0 <= n <= 10^5; integers; start < end.

Hints
-----
- Keeping the interval that ends earliest leaves the most room for the rest.
- Sort indices by end; keep an interval if it starts after (or at, for half-open) the end of
  the last kept one; everything else is removed.

Follow-ups
----------
- Minimum arrows to burst balloons (closed intervals; Chapter 20, Ex 10).
- Weighted version: greedy fails, use the DP rung with bisect.
"""
from __future__ import annotations

from bisect import bisect_right
from itertools import combinations


def _compatible(a: list[int], b: list[int], closed: bool) -> bool:
    first, second = (a, b) if a[0] <= b[0] else (b, a)
    return second[0] > first[1] if closed else second[0] >= first[1]


def brute_force(intervals: list[list[int]], closed: bool = False) -> int:
    raise NotImplementedError("TODO")


def dp(intervals: list[list[int]], closed: bool = False) -> int:
    raise NotImplementedError("TODO")


def solve(intervals: list[list[int]], closed: bool = False) -> tuple[int, list[int]]:
    raise NotImplementedError("TODO")


def wrong_by_start(intervals: list[list[int]]) -> int:
    """Tempting but WRONG (half-open): sort by start, keep whatever comes first."""
    raise NotImplementedError("TODO")


def main() -> None:
    iv = [[1, 2], [2, 3], [3, 4], [1, 3]]
    print("half-open:", solve(iv), "| closed:", solve(iv, closed=True))
    print("duplicates:", solve([[1, 2], [1, 2], [1, 2]]))
    print("empty     :", solve([]))
    trap = [[1, 10], [2, 3], [4, 5], [6, 7]]
    print("trap", trap, "-> greedy by end:", solve(trap)[0], "| wrong by start:",
          wrong_by_start(trap))
    print("dp agrees :", dp(iv) == solve(iv)[0] == brute_force(iv),
          dp(iv, True) == solve(iv, True)[0] == brute_force(iv, True))


if __name__ == "__main__":
    main()
