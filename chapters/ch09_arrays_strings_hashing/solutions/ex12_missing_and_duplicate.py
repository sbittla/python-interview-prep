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

Approach ladder
---------------
1. Brute force — for x = 1, 2, 3, ... test "x in nums". O(n^2).
2. Improved   — put everything in a set, then scan 1..n+1. O(n) time but O(n)
   extra space. Or sort: O(n log n).
3. Optimal    — the answer is in 1..n+1, so use the array itself as the hash
   table: cyclic sort places value v at index v-1 by swapping. Each swap fixes
   one value permanently, so total swaps <= n -> O(n) time, O(1) space. Then the
   first index i with nums[i] != i+1 gives i+1.

Follow-ups
----------
- Find all duplicates in 1..n: sign marking (find_duplicates_marking) — flip
  nums[v-1] negative on first sight; already negative means a repeat. Same
  O(n) time / O(1) space, no swaps, and the signs can be restored afterwards.
- All numbers disappeared: same cyclic sort, then scan mismatches.
- Not allowed to modify input? Use Floyd's cycle detection (find-the-duplicate,
  Chapter 10) or the sum / xor identity for the single-missing case.
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> int:
    x = 1
    while x in nums:                # O(n) membership test per x
        x += 1
    return x


def with_set(nums: list[int]) -> int:
    seen = set(nums)
    for x in range(1, len(nums) + 2):
        if x not in seen:
            return x
    return len(nums) + 1  # unreachable


def cyclic_sort(nums: list[int]) -> list[int]:
    """Place every v in 1..n at index v-1 (values outside range stay put)."""
    n = len(nums)
    i = 0
    while i < n:
        v = nums[i]
        if 1 <= v <= n and nums[v - 1] != v:   # != v also stops duplicate loops
            nums[i], nums[v - 1] = nums[v - 1], nums[i]
        else:
            i += 1
    return nums


def solve(nums: list[int]) -> int:
    cyclic_sort(nums)
    for i, v in enumerate(nums):
        if v != i + 1:
            return i + 1
    return len(nums) + 1


def find_error(nums: list[int]) -> tuple[int, int]:
    nums = cyclic_sort(list(nums))
    for i, v in enumerate(nums):
        if v != i + 1:
            return (v, i + 1)       # v sits in the slot of the missing value
    raise ValueError("no error found")


def find_duplicates_marking(nums: list[int]) -> list[int]:
    """Values 1..n, each appearing once or twice: return the repeated ones, sorted.

    Index-as-hash by sign marking: visiting v flips nums[v-1] negative; finding
    it already negative means v was seen before. O(n) time, O(1) extra space
    (besides the output); the signs are restored before returning.
    """
    dups = []
    for x in nums:
        v = abs(x)                      # the slot may already be flipped
        if nums[v - 1] < 0:
            dups.append(v)
        else:
            nums[v - 1] = -nums[v - 1]
    for i, x in enumerate(nums):        # undo the marks
        nums[i] = abs(x)
    return sorted(dups)


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
