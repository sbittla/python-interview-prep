"""
Exercise 07 — Largest Concatenated Number with cmp_to_key       [Tier: ★ Core]
Chapter 06 · Pattern: custom comparator via functools.cmp_to_key · Target time: 20 min

Problem
-------
Given a list of non-negative integers, arrange them so that writing them one
after another forms the largest possible number. Return it as a string with no
leading zeros (all zeros -> "0"). This is the classic "Largest Number" puzzle.

Examples
--------
>>> solve([10, 2])
'210'
>>> solve([3, 30, 34, 5, 9])
'9534330'
>>> solve([0, 0])
'0'

Constraints
-----------
- 1 <= len(nums) <= 10**4; 0 <= nums[i] <= 10**9.

Hints
-----
- `cmp_to_key` turns a function returning negative/zero/positive into a key.
- Return negative when a should come FIRST.
- Strip leading zeros at the end: "00" must become "0".

Follow-ups
----------
- A key-only version: compare `s * k` truncations (cute but harder to justify).
- Smallest number instead: flip the comparison and keep the zero handling.
- Why is the comparator transitive? (a+b > b+a compares a/(10^|a|-1) values.)
"""
from __future__ import annotations

from functools import cmp_to_key, reduce
from itertools import permutations


def brute_force(nums: list[int]) -> str:
    raise NotImplementedError("TODO")


def wrong_lexicographic(nums: list[int]) -> str:
    raise NotImplementedError("TODO")


def _cmp(a: str, b: str) -> int:
    raise NotImplementedError("TODO")


def solve(nums: list[int]) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    for nums in ([10, 2], [3, 30, 34, 5, 9], [0, 0], [3, 30, 34], [121, 12], [7]):
        print(f"{str(nums):18} solve={solve(nums):10} brute={brute_force(nums):10} "
              f"lexicographic={wrong_lexicographic(nums)}")
    # functools.reduce folds a list left to right: ((1*2)*3)*4
    print("reduce product:", reduce(lambda acc, x: acc * x, [1, 2, 3, 4], 1))


if __name__ == "__main__":
    main()
