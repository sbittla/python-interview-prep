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

Approach ladder
---------------
1. Brute force — try every subset to keep, largest conflict-free wins. O(2^n * n^2).
2. Improved   — DP: sort by end; best[i] = 1 + max best[j] over compatible j < i. O(n^2)
   (O(n log n) with binary search; this is weighted interval scheduling without weights).
3. Optimal    — greedy by earliest end. O(n log n) time, O(n) for the sorted order.
   Why move up: with equal weights, the earliest-ending choice is always safe (exchange
   argument, Chapter 20.2), so the DP table is unnecessary.

Wrong-but-tempting
------------------
- Sort by start and keep the first of each overlapping pair (see wrong_by_start: one long
  interval that starts first blocks many short ones).
- Sort by length: [1, 5], [4, 7], [6, 10] keeps the short middle one and loses two.
- Using `start >= last_end` for closed intervals (touching must conflict there).

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
    n = len(intervals)
    for keep in range(n, -1, -1):
        for subset in combinations(intervals, keep):
            if all(_compatible(x, y, closed) for x, y in combinations(subset, 2)):
                return n - keep
    return n


def dp(intervals: list[list[int]], closed: bool = False) -> int:
    order = sorted(intervals, key=lambda iv: iv[1])
    ends = [e for _, e in order]
    best = [0] * (len(order) + 1)          # best[i] = most kept among the first i by end
    for i, (s, _) in enumerate(order):
        # number of earlier intervals whose end is compatible with this start
        j = bisect_right(ends, s - 1 if closed else s, 0, i)
        best[i + 1] = max(best[i], best[j] + 1)
    return len(order) - best[-1]


def solve(intervals: list[list[int]], closed: bool = False) -> tuple[int, list[int]]:
    order = sorted(range(len(intervals)), key=lambda i: intervals[i][1])
    removed: list[int] = []
    last_end = None
    for i in order:
        s, e = intervals[i]
        if last_end is None or (s > last_end if closed else s >= last_end):
            last_end = e                   # keep: it ends earliest among the rest
        else:
            removed.append(i)
    return len(removed), sorted(removed)


def wrong_by_start(intervals: list[list[int]]) -> int:
    """Tempting but WRONG (half-open): sort by start, keep whatever comes first."""
    removed, last_end = 0, None
    for s, e in sorted(intervals):
        if last_end is None or s >= last_end:
            last_end = e
        else:
            removed += 1
    return removed


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
