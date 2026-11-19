"""
Exercise 05 — Merge intervals (closed, touching endpoints)       [Tier: ★ Core]
Chapter 17 · Pattern: sort by start, extend the last interval · Target time: 15 min

Problem
-------
Given closed intervals [start, end] (start <= end) in any order, return the union as a sorted
list of disjoint intervals. By default intervals that merely touch ([1, 2] and [2, 3]) share
the point 2 and are merged. With merge_touching=False, touching intervals stay separate
(useful when the caller treats intervals as half-open [start, end) and wants to keep
back-to-back bookings apart); genuinely overlapping ones are still merged.

Examples
--------
>>> solve([[1, 3], [8, 10], [2, 6], [15, 18]])
[[1, 6], [8, 10], [15, 18]]
>>> solve([[1, 4], [4, 5]]), solve([[1, 4], [4, 5]], merge_touching=False)
([[1, 5]], [[1, 4], [4, 5]])
>>> solve([[1, 10], [2, 3]])
[[1, 10]]

Constraints
-----------
- 0 <= n <= 10^4; integers; start <= end. The input list must not be modified.

Hints
-----
- After sorting by start, an interval can only overlap the last interval of the output.
- The new end is max(old end, current end) — a later interval can be nested inside.

Follow-ups
----------
- Stream of intervals: keep a sorted container and merge on insert (Ex 06 for one insert).
- Total covered length: sum(end - start) over the merged list.
"""
from __future__ import annotations


def _overlaps(a: list[int], b: list[int], merge_touching: bool) -> bool:
    if merge_touching:
        return a[0] <= b[1] and b[0] <= a[1]
    return a[0] < b[1] and b[0] < a[1]


def brute_force(intervals: list[list[int]], merge_touching: bool = True) -> list[list[int]]:
    raise NotImplementedError("TODO")


def solve(intervals: list[list[int]], merge_touching: bool = True) -> list[list[int]]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [
        [[1, 3], [8, 10], [2, 6], [15, 18]],
        [[1, 4], [4, 5]],
        [[1, 10], [2, 3], [4, 5]],
        [[5, 5], [5, 7]],
        [],
        [[3, 4]],
    ]
    for iv in cases:
        print(f"{str(iv):34} -> {solve(iv)}")
    print("touching kept apart:", solve([[1, 4], [4, 5], [5, 6]], merge_touching=False))
    data = [[1, 3], [2, 4]]
    solve(data)
    print("input untouched:", data)
    print("agrees with brute force:", all(solve(c) == brute_force(c) for c in cases))


if __name__ == "__main__":
    main()
