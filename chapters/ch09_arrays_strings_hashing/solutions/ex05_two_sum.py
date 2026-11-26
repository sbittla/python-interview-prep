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

Approach ladder
---------------
1. Brute force — check every pair (i, j). O(n^2) time, O(1) space.
2. Improved   — sort (value, index) pairs and use two pointers (Chapter 10).
   O(n log n) time, O(n) space; returns *a* pair but not the earliest-j one
   without extra work.
3. Optimal    — one pass with a dict value -> index: for each x, look up
   target - x among values already seen. O(n) time, O(n) space.
   Checking *before* inserting x stops us pairing an element with itself.

Follow-ups
----------
- Return all pairs of values (no duplicates)? -> ex06 / count with Counter.
- Input sorted? Two pointers with O(1) space (Chapter 10).
- Data stream with add()/find() calls: trade off which operation is O(1).
- Three-sum / k-sum: sort + two pointers (Chapter 10).
"""
from __future__ import annotations


def brute_force(nums: list[int], target: int) -> tuple[int, int] | None:
    for j in range(len(nums)):
        for i in range(j):
            if nums[i] + nums[j] == target:
                return (i, j)            # j-major order -> smallest j first
    return None


def sort_two_pointers(nums: list[int], target: int) -> tuple[int, int] | None:
    """Returns some valid pair (not necessarily smallest j)."""
    order = sorted(range(len(nums)), key=nums.__getitem__)
    lo, hi = 0, len(order) - 1
    while lo < hi:
        s = nums[order[lo]] + nums[order[hi]]
        if s == target:
            i, j = order[lo], order[hi]
            return (min(i, j), max(i, j))
        if s < target:
            lo += 1
        else:
            hi -= 1
    return None


def solve(nums: list[int], target: int) -> tuple[int, int] | None:
    seen: dict[int, int] = {}            # value -> first index where it appeared
    for j, x in enumerate(nums):
        need = target - x
        if need in seen:                 # look up BEFORE inserting x
            return (seen[need], j)
        if x not in seen:                # keep the earliest index
            seen[x] = j
    return None


def main() -> None:
    cases = [([2, 7, 11, 15], 9), ([3, 2, 4], 6), ([3, 3], 6), ([1, 2], 7),
             ([], 0), ([-3, 4, 3, 90], 0), ([5, 1, 5, 1], 6)]
    for nums, target in cases:
        print(f"nums={nums!s:<18} target={target:<3} -> {solve(nums, target)}"
              f"  brute={brute_force(nums, target)}")


if __name__ == "__main__":
    main()
