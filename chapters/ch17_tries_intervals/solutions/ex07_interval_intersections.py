"""
Exercise 07 — Intersection of two interval lists                 [Tier: ★ Core]
Chapter 17 · Pattern: two pointers over sorted intervals · Target time: 20 min

Problem
-------
A and B are each lists of closed intervals [start, end], sorted and pairwise disjoint within
their own list. Return the intersection of the two sets as a sorted list of closed intervals.
Intervals that only touch intersect in a single point: [1, 3] and [3, 5] give [3, 3].

Examples
--------
>>> solve([[0, 2], [5, 10], [13, 23], [24, 25]], [[1, 5], [8, 12], [15, 24], [25, 26]])
[[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]
>>> solve([[1, 3]], []), solve([[1, 3]], [[4, 6]])
([], [])

Constraints
-----------
- 0 <= len(A), len(B) <= 1000; integers.

Hints
-----
- Two closed intervals intersect in [max(starts), min(ends)] when that is non-empty
  (lo <= hi).
- After comparing A[i] and B[j], the one that ends first cannot meet anything else in the
  other list: advance its pointer.

Approach ladder
---------------
1. Brute force — intersect every pair: O(m * n) pairs, then sort. O(mn + k log k).
2. Optimal    — two pointers; each step advances one pointer. O(m + n) time, O(k) output.
   Why move up: both lists are sorted, so most pairs cannot possibly intersect.

Wrong-but-tempting
------------------
- `if lo < hi` instead of `lo <= hi`: drops single-point intersections like [5, 5].
- Advancing both pointers when the ends are equal is fine; advancing the one with the
  smaller START is not (it can still overlap the next interval of the other list).

Follow-ups
----------
- Half-open intervals: use `lo < hi`, since [1, 3) and [3, 5) share no point.
- Free time common to k calendars: merge all busy lists, then take the gaps.
"""
from __future__ import annotations


def brute_force(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    out = []
    for s1, e1 in a:
        for s2, e2 in b:
            lo, hi = max(s1, s2), min(e1, e2)
            if lo <= hi:
                out.append([lo, hi])
    return sorted(out)


def solve(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    i = j = 0
    out: list[list[int]] = []
    while i < len(a) and j < len(b):
        lo = max(a[i][0], b[j][0])
        hi = min(a[i][1], b[j][1])
        if lo <= hi:                       # closed: a single shared point counts
            out.append([lo, hi])
        if a[i][1] < b[j][1]:              # the interval that ends first is finished
            i += 1
        else:
            j += 1
    return out


def main() -> None:
    a = [[0, 2], [5, 10], [13, 23], [24, 25]]
    b = [[1, 5], [8, 12], [15, 24], [25, 26]]
    print("A & B         :", solve(a, b))
    print("touching      :", solve([[1, 3]], [[3, 5]]))
    print("empty / apart :", solve([[1, 3]], []), solve([[1, 3]], [[4, 6]]))
    print("nested        :", solve([[1, 10]], [[2, 3], [5, 7], [9, 12]]))
    print("agrees with brute force:", solve(a, b) == brute_force(a, b))


if __name__ == "__main__":
    main()
