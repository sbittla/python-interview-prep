"""
Exercise 12 — Cyclic Sort: Missing and Duplicate Numbers  [Tier: ◆ Extended]
Chapter 09 · Pattern: cyclic sort / index-as-hash · Target time: 25 min

Problem
-------
(a) find_error(nums): nums should contain each of 1..n exactly once, but one
    value was overwritten by a copy of another. Return (duplicate, missing).
(b) solve(nums): return the smallest positive integer that does NOT appear in an
    arbitrary list of integers ("first missing positive"), using O(n) time and
    O(1) extra space (you may modify the input).

Examples
--------
>>> find_error([1, 2, 2, 4])
(2, 3)
>>> solve([3, 4, -1, 1])
2
>>> solve([7, 8, 9])
1

Constraints
-----------
- 1 <= len(nums) <= 10**5

Hints
-----
- The first missing positive is always in 1..n+1.
- Cyclic sort: while nums[i] is in 1..n and nums[nums[i]-1] != nums[i], swap it into its home slot.
- After sorting, the first index i with nums[i] != i + 1 answers both questions.

Follow-ups
----------
- Find all numbers disappeared / all duplicates in 1..n: same cyclic sort, then
  scan mismatches.
- Not allowed to modify input? Use Floyd's cycle detection (find-the-duplicate,
  Chapter 10) or the sum / xor identity for the single-missing case.
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def with_set(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def cyclic_sort(nums: list[int]) -> list[int]:
    """Place every v in 1..n at index v-1 (values outside range stay put)."""
    raise NotImplementedError("TODO")


def solve(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def find_error(nums: list[int]) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def main() -> None:
    for nums in [[1, 2, 0], [3, 4, -1, 1], [7, 8, 9, 11, 12], [1], [2, 1], [1, 1], []]:
        print(f"first missing positive {nums!s:<18} -> {solve(list(nums))}"
              f"  (brute={brute_force(nums)}, set={with_set(nums)})")
    print("cyclic sort [3, 1, 5, 4, 2]:", cyclic_sort([3, 1, 5, 4, 2]))
    for nums in [[1, 2, 2, 4], [3, 2, 3, 4, 6, 5], [2, 2]]:
        print(f"find_error {nums} -> (duplicate, missing) = {find_error(nums)}")


if __name__ == "__main__":
    main()
