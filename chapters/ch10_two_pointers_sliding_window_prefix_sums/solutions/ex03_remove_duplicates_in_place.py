"""
Exercise 03 — Keep At Most k Copies, In Place            [Tier: ★ Core]
Chapter 10 · Pattern: same-direction read/write pointers · Target time: 15 min

Problem
-------
nums is sorted in non-decreasing order. Rearrange it in place so that its first
m positions hold the same values in the same order, but with every value kept
at most k times (k >= 1). Return m. What is left after position m does not
matter. Use O(1) extra space.

Examples
--------
>>> a = [1, 1, 1, 2, 2, 3]; m = solve(a, 2); a[:m]
[1, 1, 2, 2, 3]
>>> a = [0, 0, 1, 1, 1, 2]; m = solve(a, 1); a[:m]
[0, 1, 2]

Constraints
-----------
- 0 <= len(nums) <= 3 * 10**4; nums sorted; 1 <= k.

Approach ladder
---------------
1. Brute force — scan and `del nums[i]` whenever a value is over its quota.
   Each delete shifts the tail: O(n^2) time worst case, O(1) space.
2. Improved   — build a fresh filtered list, then copy it back. O(n) time but
   O(n) extra space, which the problem forbids.
3. Optimal    — the loop variable reads every element; write pointer w marks
   the end of the kept prefix. Because nums is sorted, x may be kept iff
   w < k or nums[w - k] != x (the value k slots back in the *kept* prefix
   differs). O(n) time, O(1) space.

Invariant: after reading nums[:r], nums[:w] is the correct answer for it.

Wrong-but-tempting
------------------
- Comparing with nums[r - k] (the read side) instead of nums[w - k]: once the
  writer has overwritten slot r - k with a later value, the check sees a
  "duplicate" that was never there and drops copies that should be kept
  ([1, 1, 1, 2, 2] with k = 2 gives [1, 1, 2]).

Follow-ups
----------
- Move zeroes / remove a value: same read/write idea (Chapter 9, ex01).
- Unsorted input: needs a Counter, and O(n) space.
"""
from __future__ import annotations


def brute_force(nums: list[int], k: int) -> int:
    i = 0
    while i < len(nums):
        if i >= k and nums[i] == nums[i - k]:
            del nums[i]                   # O(n) shift every time
        else:
            i += 1
    return len(nums)


def copy_filter(nums: list[int], k: int) -> int:
    kept: list[int] = []
    for x in nums:
        if len(kept) < k or kept[-k] != x:
            kept.append(x)
    nums[:len(kept)] = kept               # O(n) extra space for `kept`
    return len(kept)


def wrong_read_side(nums: list[int], k: int) -> int:
    """Wrong-but-tempting: compares with the read side nums[r - k]."""
    w = 0
    for r in range(len(nums)):
        x = nums[r]
        if r < k or nums[r - k] != x:
            nums[w] = x
            w += 1
    return w


def solve(nums: list[int], k: int) -> int:
    w = 0                                 # nums[:w] is the kept prefix
    for x in nums:                        # read pointer is implicit
        if w < k or nums[w - k] != x:
            nums[w] = x
            w += 1
    return w


def main() -> None:
    cases = [([1, 1, 1, 2, 2, 3], 2), ([0, 0, 1, 1, 1, 1, 2, 3, 3], 2), ([0, 0, 1, 1, 1, 2], 1),
             ([], 1), ([7], 3), ([2, 2, 2, 2], 1), ([1, 1, 2, 2, 2, 3, 3, 3], 1)]
    for nums, k in cases:
        a, b = list(nums), list(nums)
        m, w = solve(a, k), wrong_read_side(b, k)
        print(f"nums={nums!s:<29} k={k} -> {a[:m]!s:<22} m={m}"
              f"  read-side(wrong)={b[:w]}")


if __name__ == "__main__":
    main()
