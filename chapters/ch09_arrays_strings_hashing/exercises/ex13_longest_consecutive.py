"""
Exercise 13 — Longest Consecutive Run (set membership)    [Tier: ★ Core]
Chapter 09 · Pattern: set-based membership · Target time: 15 min

Problem
-------
Given an unsorted list of integers, return the length of the longest run of
consecutive integer values (e.g. 4, 5, 6, 7) that all appear in the list.
Order in the list does not matter and duplicates count once. Also implement
contains_duplicate(nums) -> bool.

Examples
--------
>>> solve([100, 4, 200, 1, 3, 2])
4
>>> solve([])
0

Constraints
-----------
- 0 <= len(nums) <= 10**5; values in [-10**9, 10**9].

Hints
-----
- Put values in a set for O(1) membership.
- Only start counting at x when x - 1 is not in the set.
- Each value is walked over at most once in total, so the nested loop is still O(n).

Follow-ups
----------
- Return the run itself, not just its length.
- Streaming inserts: union-find or a dict of run endpoints (Chapter 16).
- Why is the nested loop still O(n)? Amortised argument: each element is the
  "next" of at most one run walk.
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def by_sorting(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def solve(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def contains_duplicate(nums: list[int]) -> bool:
    raise NotImplementedError("TODO")


def first_duplicate(nums: list[int]):
    """Early-exit variant: returns the first value seen twice, else None."""
    raise NotImplementedError("TODO")


def main() -> None:
    for nums in [[100, 4, 200, 1, 3, 2], [0, 3, 7, 2, 5, 8, 4, 6, 0, 1], [], [5], [1, 2, 0, 1], [-2, -1, 9]]:
        print(f"{nums!s:<32} longest={solve(nums)} brute={brute_force(nums)} sorted={by_sorting(nums)}")
    print("contains_duplicate([1,2,3,1]):", contains_duplicate([1, 2, 3, 1]))
    print("first_duplicate([2, 5, 1, 5, 2]):", first_duplicate([2, 5, 1, 5, 2]))
    a, b = {1, 2, 3, 4}, {3, 4, 5}
    print("intersection:", sorted(a & b), "union:", sorted(a | b), "a-b:", sorted(a - b), "xor:", sorted(a ^ b))


if __name__ == "__main__":
    main()
