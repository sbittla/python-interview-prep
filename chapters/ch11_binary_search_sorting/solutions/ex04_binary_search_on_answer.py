"""
Exercise 04 — Binary Search on the Answer                          [Tier: ★ Core]
Chapter 11 · Pattern: monotonic feasibility + "first True" search · Target time: 20 min

Problem
-------
(a) Minimum processing rate. A worker must finish several piles of tasks within
h hours. In one hour the worker picks a single pile and completes up to k tasks
from it (if the pile has fewer, the rest of the hour is wasted). Return the
smallest integer rate k that finishes every pile within h hours.

(b) Minimum truck capacity. Packages with given weights must be shipped in
order, within `days` days, one truck trip per day. Return the smallest truck
capacity that makes this possible. (Same shape as "split an array into m
parts minimising the largest part sum".)

Examples
--------
>>> solve([3, 6, 7, 11], 8)
4
>>> min_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5)
15

Constraints
-----------
- 1 <= len(piles) <= h <= 10^9; 1 <= piles[i] <= 10^9.
- 1 <= days <= len(weights).

Approach ladder
---------------
1. Brute force — try k = 1, 2, 3, ... until feasible. O(max(piles) * n).
2. Improved   — notice feasible(k) is monotonic: if k works, every k' > k
   works. So the answers look like F F F F T T T T over k.
3. Optimal    — binary search the first True over [1, max(piles)].
   O(n log max(piles)). The search range is the answer space, not the array.

Follow-ups
----------
- Why hi = max(piles)? At that rate every pile takes one hour, and h >= n.
- Floating-point answers (e.g. minimise max distance): loop a fixed number of
  iterations (e.g. 60-100) or until hi - lo < eps.
- Maximise instead of minimise (e.g. "largest minimum distance"): search the
  last True of a T T T F F F predicate.
"""
from __future__ import annotations

from typing import Callable


def first_true(lo: int, hi: int, pred: Callable[[int], bool]) -> int:
    """Smallest x in [lo, hi] with pred(x) True, assuming pred is F..F T..T.
    Returns hi + 1 if pred is never True. Invariant: pred(hi+1) is treated as True,
    everything < lo is known False."""
    hi += 1
    while lo < hi:
        mid = (lo + hi) // 2
        if pred(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def hours_needed(piles: list[int], k: int) -> int:
    return sum((p + k - 1) // k for p in piles)   # integer ceil(p / k)


def brute_force(piles: list[int], h: int) -> int:
    k = 1
    while hours_needed(piles, k) > h:
        k += 1
    return k


def solve(piles: list[int], h: int) -> int:
    return first_true(1, max(piles), lambda k: hours_needed(piles, k) <= h)


def days_needed(weights: list[int], cap: int) -> int:
    days, load = 1, 0
    for w in weights:
        if load + w > cap:
            days += 1
            load = 0
        load += w
    return days


def min_capacity(weights: list[int], days: int) -> int:
    # lower bound: the heaviest package must fit; upper bound: ship all in one day
    return first_true(max(weights), sum(weights), lambda c: days_needed(weights, c) <= days)


def max_min_distance(positions: list[int], m: int) -> int:
    """'Maximise the minimum': place m items at given positions so the smallest
    gap is as large as possible. Predicate can_place(d) is T..T F..F, so we
    search the last True."""
    pos = sorted(positions)

    def can_place(d: int) -> bool:
        count, last = 1, pos[0]
        for p in pos[1:]:
            if p - last >= d:
                count += 1
                last = p
        return count >= m

    lo, hi = 1, pos[-1] - pos[0]
    while lo < hi:
        mid = (lo + hi + 1) // 2      # upper mid: avoids infinite loop when lo = mid
        if can_place(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


def main() -> None:
    piles, h = [3, 6, 7, 11], 8
    print("piles", piles, "h", h)
    for k in range(1, 8):
        print(f"  k={k}: hours={hours_needed(piles, k):>2} feasible={hours_needed(piles, k) <= h}")
    print("min rate (binary search):", solve(piles, h), " brute:", brute_force(piles, h))
    print("min rate [30,11,23,4,20], h=5:", solve([30, 11, 23, 4, 20], 5))
    print("min rate [30,11,23,4,20], h=6:", solve([30, 11, 23, 4, 20], 6))
    print("one huge pile [10**9], h=2:", solve([10**9], 2))
    weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print("min capacity, 5 days:", min_capacity(weights, 5))
    print("min capacity, 1 day:", min_capacity(weights, 1))
    print("min capacity, 10 days:", min_capacity(weights, 10))
    print("max min distance [1,2,3,4,7], m=3:", max_min_distance([1, 2, 3, 4, 7], 3))
    print("first_true on x*x >= 50 in [0, 50]:", first_true(0, 50, lambda x: x * x >= 50))


if __name__ == "__main__":
    main()
