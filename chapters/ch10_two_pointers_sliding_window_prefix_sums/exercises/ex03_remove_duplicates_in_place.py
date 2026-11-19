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

Hints
-----
- Keep a write index w; nums[:w] is the answer so far.
- Sorted input: x is over quota exactly when nums[w - k] == x (look at the KEPT prefix).

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
    raise NotImplementedError("TODO")


def copy_filter(nums: list[int], k: int) -> int:
    raise NotImplementedError("TODO")


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
    raise NotImplementedError("TODO")


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
