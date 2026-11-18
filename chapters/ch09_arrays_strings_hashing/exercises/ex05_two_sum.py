"""
Exercise 05 — Two Sum (unsorted)                         [Tier: ★ Core]
Chapter 09 · Pattern: hash map complement lookup · Target time: 10 min

Problem
-------
Given an unsorted list of integers and a target, return the indices (i, j) with
i < j of two different positions whose values add up to target. If several pairs
exist, return the one whose j is smallest (the first pair "completed" in a
left-to-right scan). Return None if no pair exists.

Examples
--------
>>> solve([2, 7, 11, 15], 9)
(0, 1)
>>> solve([3, 3], 6)
(0, 1)
>>> solve([1, 2], 7) is None
True

Constraints
-----------
- 0 <= len(nums) <= 10**5; values and target may be negative.

Hints
-----
- For each x you need target - x. Have you already seen it?
- Store value -> index in a dict; look up the complement BEFORE inserting x.
- Keep the earliest index for repeated values.

Follow-ups
----------
- Return all pairs of values (no duplicates)? -> ex06 / count with Counter.
- Input sorted? Two pointers with O(1) space (Chapter 10).
- Data stream with add()/find() calls: trade off which operation is O(1).
- Three-sum / k-sum: sort + two pointers (Chapter 10).
"""
from __future__ import annotations


def brute_force(nums: list[int], target: int) -> tuple[int, int] | None:
    raise NotImplementedError("TODO")


def sort_two_pointers(nums: list[int], target: int) -> tuple[int, int] | None:
    """Returns some valid pair (not necessarily smallest j)."""
    raise NotImplementedError("TODO")


def solve(nums: list[int], target: int) -> tuple[int, int] | None:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [([2, 7, 11, 15], 9), ([3, 2, 4], 6), ([3, 3], 6), ([1, 2], 7),
             ([], 0), ([-3, 4, 3, 90], 0), ([5, 1, 5, 1], 6)]
    for nums, target in cases:
        print(f"nums={nums!s:<18} target={target:<3} -> {solve(nums, target)}"
              f"  brute={brute_force(nums, target)}")


if __name__ == "__main__":
    main()
