"""
Exercise 06 — Insert an interval into a sorted disjoint list     [Tier: ★ Core]
Chapter 17 · Pattern: three-phase linear scan · Target time: 15 min

Problem
-------
`intervals` is a list of closed intervals [start, end], sorted by start and pairwise
disjoint (they do not even touch). Insert `new` and return the list in the same form,
merging every interval that overlaps or touches `new`. Do not modify the input.

Examples
--------
>>> solve([[1, 3], [6, 9]], [2, 5])
[[1, 5], [6, 9]]
>>> solve([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8])
[[1, 2], [3, 10], [12, 16]]
>>> solve([[1, 2], [5, 6]], [2, 5])
[[1, 6]]

Constraints
-----------
- 0 <= n <= 10^4; new[0] <= new[1]; integers.

Hints
-----
- Three phases: copy intervals that end before new starts; absorb every interval that starts
  at or before new ends; copy the rest.
- "Ends before" for closed, touching-merges: end < new_start (strict).

Follow-ups
----------
- Remove an interval instead (may split one interval into two).
- Many inserts: use a sorted container keyed by start (Chapter 11) or an interval tree.
"""
from __future__ import annotations


def merge(intervals: list[list[int]]) -> list[list[int]]:
    out: list[list[int]] = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def brute_force(intervals: list[list[int]], new: list[int]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def solve(intervals: list[list[int]], new: list[int]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [
        ([[1, 3], [6, 9]], [2, 5]),
        ([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]),
        ([[1, 2], [5, 6]], [2, 5]),
        ([], [4, 7]),
        ([[1, 2]], [5, 6]),
        ([[5, 6]], [1, 2]),
        ([[3, 4]], [0, 9]),
    ]
    for iv, new in cases:
        print(f"{str(iv):38} + {str(new):7} -> {solve(iv, new)}")
    print("agrees with brute force:", all(solve(a, b) == brute_force(a, b) for a, b in cases))


if __name__ == "__main__":
    main()
