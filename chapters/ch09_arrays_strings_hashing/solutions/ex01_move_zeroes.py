"""
Exercise 01 — Move Zeroes to the End                    [Tier: ★ Core]
Chapter 09 · Pattern: in-place write pointer · Target time: 10 min

Problem
-------
Given a list of integers, move every 0 to the end of the list while keeping the
relative order of the non-zero values. Do it in place (O(1) extra space). For
convenience, return the same list object after modifying it.

Examples
--------
>>> solve([0, 1, 0, 3, 12])
[1, 3, 12, 0, 0]
>>> solve([0])
[0]

Constraints
-----------
- 0 <= len(nums) <= 10**5
- Values are any integers; only exact 0 is moved.

Approach ladder
---------------
1. Brute force — build a new list of non-zeros, pad with zeros, copy back.
   O(n) time but O(n) extra space; violates the in-place requirement.
2. Improved   — bubble each zero rightwards with adjacent swaps. In place, but
   O(n^2) time in the worst case (many zeros at the front).
3. Optimal    — a "write" pointer: copy each non-zero to nums[write], then fill
   the tail with zeros (or swap, which writes fewer times). O(n) time, O(1) space.
   We move up because rung 1 breaks the space constraint and rung 2 is quadratic.

Follow-ups
----------
- Minimise the number of writes (swap only when read != write).
- Move all values equal to a given target, or all negatives, to the end.
- Stable partition by any predicate (this is the same template).
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> list[int]:
    """O(n) extra space: rebuild then copy back."""
    non_zero = [x for x in nums if x != 0]
    nums[:] = non_zero + [0] * (len(nums) - len(non_zero))
    return nums


def bubble(nums: list[int]) -> list[int]:
    """In place but O(n^2): repeatedly swap a zero with its right neighbour."""
    n = len(nums)
    for i in range(n):
        for j in range(n - 1 - i):
            if nums[j] == 0 and nums[j + 1] != 0:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
    return nums


def solve(nums: list[int]) -> list[int]:
    """Write-pointer swap: O(n) time, O(1) space, stable for non-zeros."""
    write = 0                      # next slot for a non-zero value
    for read in range(len(nums)):
        if nums[read] != 0:
            if read != write:      # avoid useless self-swaps
                nums[write], nums[read] = nums[read], nums[write]
            write += 1
    return nums


def main() -> None:
    cases = [[0, 1, 0, 3, 12], [0], [], [1, 2, 3], [0, 0, 1], [4, 0, -2, 0, 0, 7]]
    for case in cases:
        a, b, c = list(case), list(case), list(case)
        print(f"{case!s:<22} -> {solve(a)}  (brute={brute_force(b) == a}, bubble={bubble(c) == a})")


if __name__ == "__main__":
    main()
