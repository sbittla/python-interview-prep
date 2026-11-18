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

Hints
-----
- out[i] = (product of everything left of i) * (product of everything right of i).
- First pass left-to-right stores the left products in out; second pass right-to-left multiplies a running suffix in.
- with_division must handle 0, 1 and 2+ zeros separately.

Follow-ups
----------
- Why not division? Zeros, and in fixed-width languages, precision/overflow.
- Can you do it with O(1) extra space? (Yes — the output list does not count.)
- Same idea: "sum except self", "max of everything except i" (prefix/suffix max).
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def with_division(nums: list[int]) -> list[int]:
    """The tempting O(n) shortcut, made correct by counting zeros."""
    raise NotImplementedError("TODO")


def solve(nums: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    for case in [[1, 2, 3, 4], [2, 0, 5], [0, 0, 3], [-1, 1, 0, -3, 3], [5, 7]]:
        print(f"{case!s:<18} -> {solve(case)}  agree={solve(case) == brute_force(case) == with_division(case)}")


if __name__ == "__main__":
    main()
