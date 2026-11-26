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
(c) find_duplicates_marking(nums): values in 1..n, each once or twice; return
    the repeated values in O(n) time and O(1) extra space, restoring nums.

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
- The answer to first-missing-positive lies in a small range. Which one?
- If the list were sorted with each v at index v - 1, how would you read the answer off?
- Watch for an infinite loop when a value's home already holds that value.
- find_duplicates_marking: the sign of a number is a spare bit you can borrow.

Follow-ups
----------
- Find all duplicates in 1..n without swapping (find_duplicates_marking).
- All numbers disappeared: what does your scan see after placing values?
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


def find_duplicates_marking(nums: list[int]) -> list[int]:
    """Values 1..n, each appearing once or twice: return the repeated ones, sorted.
    O(n) time, O(1) extra space; leave nums as you found it."""
    raise NotImplementedError("TODO")


def main() -> None:
    for nums in [[1, 2, 0], [3, 4, -1, 1], [7, 8, 9, 11, 12], [1], [2, 1], [1, 1], []]:
        print(f"first missing positive {nums!s:<18} -> {solve(list(nums))}"
              f"  (brute={brute_force(nums)}, set={with_set(nums)})")
    print("cyclic sort [3, 1, 5, 4, 2]:", cyclic_sort([3, 1, 5, 4, 2]))
    for nums in [[1, 2, 2, 4], [3, 2, 3, 4, 6, 5], [2, 2]]:
        print(f"find_error {nums} -> (duplicate, missing) = {find_error(nums)}")
    nums = [4, 3, 2, 7, 8, 2, 3, 1]
    print(f"sign-marking duplicates {nums} -> {find_duplicates_marking(nums)}  restored: {nums}")


if __name__ == "__main__":
    main()
