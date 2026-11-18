"""
Exercise 02 — Product of Array Except Self               [Tier: ★ Core]
Chapter 09 · Pattern: prefix/suffix passes · Target time: 20 min

Problem
-------
Given a list of integers nums, return a list out where out[i] is the product of
every element of nums except nums[i]. Do not use division (the input may contain
zeros) and aim for O(n) time.

Examples
--------
>>> solve([1, 2, 3, 4])
[24, 12, 8, 6]
>>> solve([2, 0, 5])
[0, 10, 0]

Constraints
-----------
- 2 <= len(nums) <= 10**5
- Python ints do not overflow, but the "no division" rule still holds.

Approach ladder
---------------
1. Brute force — for each i multiply all j != i. O(n^2) time, O(1) extra.
2. Improved   — total product divided by nums[i]. O(n) but breaks on zeros and
   is forbidden by the problem; needs special-casing of 0, 1, 2+ zeros.
3. Optimal    — out[i] = (product of everything left of i) * (product of
   everything right of i). One left-to-right pass writes the prefix products,
   one right-to-left pass multiplies in a running suffix. O(n) time, O(1) extra
   space beyond the output.

Follow-ups
----------
- Why not division? Zeros, and in fixed-width languages, precision/overflow.
- Can you do it with O(1) extra space? (Yes — the output list does not count.)
- Same idea: "sum except self", "max of everything except i" (prefix/suffix max).
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> list[int]:
    out = []
    for i in range(len(nums)):
        p = 1
        for j, x in enumerate(nums):
            if j != i:
                p *= x
        out.append(p)
    return out


def with_division(nums: list[int]) -> list[int]:
    """The tempting O(n) shortcut, made correct by counting zeros."""
    zeros = nums.count(0)
    prod = 1
    for x in nums:
        if x != 0:
            prod *= x
    if zeros > 1:
        return [0] * len(nums)
    if zeros == 1:
        return [prod if x == 0 else 0 for x in nums]
    return [prod // x for x in nums]


def solve(nums: list[int]) -> list[int]:
    n = len(nums)
    out = [1] * n
    left = 1
    for i in range(n):            # out[i] = product of nums[:i]
        out[i] = left
        left *= nums[i]
    right = 1
    for i in range(n - 1, -1, -1):  # multiply in product of nums[i+1:]
        out[i] *= right
        right *= nums[i]
    return out


def main() -> None:
    for case in [[1, 2, 3, 4], [2, 0, 5], [0, 0, 3], [-1, 1, 0, -3, 3], [5, 7]]:
        print(f"{case!s:<18} -> {solve(case)}  agree={solve(case) == brute_force(case) == with_division(case)}")


if __name__ == "__main__":
    main()
