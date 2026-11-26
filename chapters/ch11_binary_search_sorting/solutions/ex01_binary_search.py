"""
Exercise 01 — Classic Binary Search with Loop Invariants          [Tier: ★ Core]
Chapter 11 · Pattern: binary search (exact match) · Target time: 10 min

Problem
-------
Given a list of integers sorted in non-decreasing order and a target value,
return the index of the target, or -1 if it is absent. Your solution must run
in O(log n) time. Write it twice: once with a closed interval [lo, hi] and once
with a half-open interval [lo, hi), and be able to state the loop invariant of each.

Examples
--------
>>> solve([-3, 0, 4, 7, 9, 12], 7)
3
>>> solve([-3, 0, 4, 7, 9, 12], 5)
-1
>>> solve([], 1)
-1

Constraints
-----------
- 0 <= len(nums) <= 10^5, nums sorted ascending, values distinct.
- If values repeat, any matching index is acceptable (see Exercise 02 for first/last).

Approach ladder
---------------
1. Brute force — scan left to right, O(n) time, O(1) space. Ignores sortedness.
2. Improved   — recursive binary search, O(log n) time but O(log n) call stack.
3. Optimal    — iterative binary search, O(log n) time, O(1) space.
   Invariant (closed): if target is present, its index lies in [lo, hi].
   Each step discards half of the candidates while preserving the invariant;
   when lo > hi the interval is empty, so the target is absent.

Wrong-but-tempting
------------------
- Closed interval but `while lo < hi`: the last one-element interval is never
  examined, so solve([5], 5) returns -1 (see wrong_closed_lt).
- Closed interval with `hi = mid` instead of `hi = mid - 1`: when lo == hi the
  interval never shrinks and the loop spins forever.
- Starting `hi = len(nums)` in the closed form: nums[mid] can read past the end.
- Copying `mid = (lo + hi) / 2` from another language: `/` returns a float in
  Python; use `//`. In C/Java with 32-bit ints, lo + hi can overflow, hence
  the habit `lo + (hi - lo) // 2` (see mid_int32).

Follow-ups
----------
- Return the insertion point instead of -1 (lower bound, Exercise 02).
- What if the list is huge and stored on disk? (Same algorithm; reads are the cost.)
- What if the size is unknown (an infinite stream sorted ascending)? Exponential
  search: double hi until nums[hi] >= target, then binary search in [hi/2, hi].
"""
from __future__ import annotations

import ctypes


def brute_force(nums: list[int], target: int) -> int:
    for i, x in enumerate(nums):
        if x == target:
            return i
    return -1


def search_recursive(nums: list[int], target: int, lo: int = 0, hi: int | None = None) -> int:
    if hi is None:
        hi = len(nums) - 1
    if lo > hi:                       # empty interval: not found
        return -1
    mid = (lo + hi) // 2
    if nums[mid] == target:
        return mid
    if nums[mid] < target:
        return search_recursive(nums, target, mid + 1, hi)
    return search_recursive(nums, target, lo, mid - 1)


def solve(nums: list[int], target: int) -> int:
    """Closed interval [lo, hi]. Invariant: target, if present, is in nums[lo..hi]."""
    lo, hi = 0, len(nums) - 1
    while lo <= hi:                   # interval non-empty
        mid = (lo + hi) // 2          # Python ints never overflow; (lo+hi)//2 is safe
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1              # target cannot be at mid or left of it
        else:
            hi = mid - 1              # target cannot be at mid or right of it
    return -1


def search_half_open(nums: list[int], target: int) -> int:
    """Half-open interval [lo, hi). Invariant: target, if present, is in nums[lo:hi]."""
    lo, hi = 0, len(nums)
    while lo < hi:                    # interval non-empty
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid                  # hi is exclusive, so mid is excluded
    return -1


def wrong_closed_lt(nums: list[int], target: int) -> int:
    """Wrong-but-tempting: closed interval [lo, hi] with a half-open loop test."""
    lo, hi = 0, len(nums) - 1
    while lo < hi:                    # bug: skips the final lo == hi candidate
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def mid_int32(lo: int, hi: int) -> tuple[int, int]:
    """What (lo + hi) // 2 and lo + (hi - lo) // 2 give with C 32-bit int arithmetic."""
    naive = ctypes.c_int32(lo + hi).value // 2        # wraps around like C int
    safe = lo + ctypes.c_int32(hi - lo).value // 2
    return naive, safe


def exponential_search(nums: list[int], target: int) -> int:
    """For 'unknown size' variants: grow the bound, then binary search inside it."""
    if not nums:
        return -1
    hi = 1
    while hi < len(nums) and nums[hi] < target:
        hi *= 2
    lo, hi = hi // 2, min(hi, len(nums) - 1)
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def trace(nums: list[int], target: int) -> list[str]:
    """Return a dry-run trace of the closed-interval search (for the book)."""
    lines = []
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            lines.append(f"lo={lo} hi={hi} mid={mid} nums[mid]={nums[mid]} -> found")
            return lines
        move = "lo=mid+1" if nums[mid] < target else "hi=mid-1"
        lines.append(f"lo={lo} hi={hi} mid={mid} nums[mid]={nums[mid]} -> {move}")
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    lines.append(f"lo={lo} hi={hi} -> empty interval, return -1")
    return lines


def main() -> None:
    nums = [-3, 0, 4, 7, 9, 12, 15, 20]
    print("nums:", nums)
    for t in (7, -3, 20, 5, 100, -10):
        results = (brute_force(nums, t), search_recursive(nums, t), solve(nums, t),
                   search_half_open(nums, t), exponential_search(nums, t))
        print(f"target={t:>4}: brute/recursive/closed/half-open/exponential = {results}")
    print("empty list:", solve([], 1), search_half_open([], 1))
    print("single element hit/miss:", solve([5], 5), solve([5], 4))
    print("wrong_closed_lt on [5], 5:", wrong_closed_lt([5], 5), "(should be 0)")
    print("all duplicates [2,2,2,2] find 2 -> some index:", solve([2, 2, 2, 2], 2))
    lo, hi = 2_000_000_000, 2_100_000_000
    print("Python mid of 2.0e9 and 2.1e9:", (lo + hi) // 2)
    print("C int32 naive / safe mid:", mid_int32(lo, hi))
    print("\nTrace for target 9:")
    for line in trace(nums, 9):
        print("  " + line)
    print("Trace for target 5:")
    for line in trace(nums, 5):
        print("  " + line)


if __name__ == "__main__":
    main()
