"""
Exercise 04 — Three-Way Partition (Dutch National Flag)  [Tier: ◆ Extended]
Chapter 10 · Pattern: same-direction pointers, three regions · Target time: 20 min

Problem
-------
Rearrange nums in place around a pivot value so that every element < pivot
comes first, then every element == pivot, then every element > pivot. Return
the pair (lt, gt) such that nums[:lt] < pivot, nums[lt:gt] == pivot and
nums[gt:] > pivot. Do it in one pass with O(1) extra space. (The classic
"sort colours" problem is the special case nums in {0, 1, 2}, pivot = 1.)

Examples
--------
>>> a = [2, 0, 2, 1, 1, 0]; solve(a, 1), a
((2, 4), [0, 0, 1, 1, 2, 2])
>>> a = [5]; solve(a, 9), a
((1, 1), [5])

Constraints
-----------
- 0 <= len(nums) <= 10**5; any integers; pivot need not occur in nums.

Hints
-----
- Four regions: < pivot, == pivot, unknown, > pivot. Shrink the unknown region.
- After swapping with the right end, the incoming element is unexamined: don't advance i.

Wrong-but-tempting
------------------
- Advancing i after swapping with the right side: the swapped-in element is
  never checked, so a small value can be stranded in the middle:
  [1, 2, 0] with pivot 1 ends as [1, 0, 2].

Follow-ups
----------
- Quicksort with many duplicates: three-way partition avoids O(n^2) on
  all-equal input (-> Chapter 11.7).
- Stable version: not possible in O(1) space with one pass; use the
  collect-and-concatenate rung.
"""
from __future__ import annotations


def _bounds(nums: list[int], pivot: int) -> tuple[int, int]:
    lt = sum(1 for x in nums if x < pivot)
    return lt, lt + sum(1 for x in nums if x == pivot)


def brute_force(nums: list[int], pivot: int) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def two_pass(nums: list[int], pivot: int) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def wrong_advance_after_swap(nums: list[int], pivot: int) -> tuple[int, int]:
    """Wrong-but-tempting: advances i after swapping with the right end."""
    lt, i, gt = 0, 0, len(nums)
    while i < gt:
        if nums[i] < pivot:
            nums[lt], nums[i] = nums[i], nums[lt]
            lt += 1
        elif nums[i] > pivot:
            gt -= 1
            nums[i], nums[gt] = nums[gt], nums[i]
        i += 1                            # bug: skips the swapped-in element
    return lt, gt


def solve(nums: list[int], pivot: int) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [([2, 0, 2, 1, 1, 0], 1), ([1, 2, 0], 1), ([5], 9), ([], 0),
             ([3, 3, 3], 3), ([9, -1, 4, 4, 7, 0, 4, 12], 4)]
    for nums, pivot in cases:
        a, b = list(nums), list(nums)
        res = solve(a, pivot)
        wrong = wrong_advance_after_swap(b, pivot)
        print(f"nums={nums!s:<26} pivot={pivot} -> {a!s:<26} (lt, gt)={res}"
              f"  advance-after-swap(wrong)={b}")


if __name__ == "__main__":
    main()
