"""
Exercise 03 — Search in a Rotated Sorted Array                     [Tier: ★ Core]
Chapter 11 · Pattern: binary search with a "which half is sorted?" test · Target time: 20 min

Problem
-------
A strictly increasing list was rotated at an unknown pivot, e.g. [0,1,2,4,5,6,7]
became [4,5,6,7,0,1,2]. (1) Return the minimum element. (2) Return the index of
target or -1. Both in O(log n). (3) Extension: if duplicates are allowed, report
whether target is present.

Examples
--------
>>> find_min([4, 5, 6, 7, 0, 1, 2])
0
>>> solve([4, 5, 6, 7, 0, 1, 2], 0)
4
>>> solve([4, 5, 6, 7, 0, 1, 2], 3)
-1

Constraints
-----------
- 1 <= len(nums) <= 5000 for find_min; 0 <= len(nums) for solve.
- Distinct values (except in search_with_duplicates).

Approach ladder
---------------
1. Brute force — linear scan, O(n).
2. Improved   — two passes: binary-search the rotation point (index of the
   minimum), then binary-search the correct sorted half. O(log n), two loops.
3. Optimal    — one pass: at every mid, at least one half [lo..mid] or
   [mid..hi] is sorted. Check whether target lies inside the sorted half's
   range; if yes go there, else go to the other half. O(log n), O(1).

Follow-ups
----------
- Duplicates: when nums[lo] == nums[mid] == nums[hi] we cannot tell which half
  is sorted; shrink lo += 1, hi -= 1. Worst case becomes O(n) (e.g. [1,1,1,1,0,1]).
- How many times was the array rotated? -> index of the minimum.
"""
from __future__ import annotations

from bisect import bisect_left


def brute_force(nums: list[int], target: int) -> int:
    return nums.index(target) if target in nums else -1


def find_min_index(nums: list[int]) -> int:
    """Index of the minimum. Compare mid with hi (not lo!)."""
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1          # minimum is strictly right of mid
        else:
            hi = mid              # mid could be the minimum
    return lo


def find_min(nums: list[int]) -> int:
    return nums[find_min_index(nums)]


def two_pass(nums: list[int], target: int) -> int:
    if not nums:
        return -1
    pivot = find_min_index(nums)
    # choose the sorted run that could contain target
    if pivot > 0 and nums[0] <= target <= nums[pivot - 1]:
        lo, hi = 0, pivot
    else:
        lo, hi = pivot, len(nums)
    i = bisect_left(nums, target, lo, hi)
    return i if i < hi and nums[i] == target else -1


def solve(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:                 # left half [lo..mid] is sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                     # right half [mid..hi] is sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


def search_with_duplicates(nums: list[int], target: int) -> bool:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return True
        if nums[lo] == nums[mid] == nums[hi]:
            lo += 1                               # cannot decide; shrink both ends
            hi -= 1
        elif nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return False


def main() -> None:
    base = [0, 1, 2, 4, 5, 6, 7]
    for k in (0, 3, 6):
        nums = base[k:] + base[:k]
        print(f"rotated by {k}: {nums} min={find_min(nums)} rotations={find_min_index(nums)}")
    nums = [4, 5, 6, 7, 0, 1, 2]
    for t in (0, 4, 2, 7, 3, 8):
        print(f"target={t}: one-pass={solve(nums, t)} two-pass={two_pass(nums, t)} "
              f"brute={brute_force(nums, t)}")
    print("single [1] find 1 / 0:", solve([1], 1), solve([1], 0))
    print("two elements [3,1] find 1:", solve([3, 1], 1))
    print("empty:", solve([], 5))
    print("duplicates [2,5,6,0,0,1,2] has 0:", search_with_duplicates([2, 5, 6, 0, 0, 1, 2], 0))
    print("duplicates [2,5,6,0,0,1,2] has 3:", search_with_duplicates([2, 5, 6, 0, 0, 1, 2], 3))
    print("duplicates [1,1,1,1,0,1] has 0:", search_with_duplicates([1, 1, 1, 1, 0, 1], 0))


if __name__ == "__main__":
    main()
