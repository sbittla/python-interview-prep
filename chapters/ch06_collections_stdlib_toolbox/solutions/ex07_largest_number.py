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

Approach ladder
---------------
1. Brute force — try every permutation, keep the max: O(n! * n). Only n <= 8.
2. Tempting but WRONG — sort the strings in reverse lexicographic order.
   It fails when one number is a prefix of another: [3, 30, 34] gives
   "34303" but "34330" is larger ("3" must precede "30").
3. Optimal    — a goes before b iff a+b > b+a as strings. This order is a
   valid total preorder, so sort with `key=cmp_to_key(cmp)`: O(n log n)
   comparisons, each O(L) for digit length L.

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
    best = max("".join(p) for p in permutations(map(str, nums)))
    return str(int(best))


def wrong_lexicographic(nums: list[int]) -> str:
    return str(int("".join(sorted(map(str, nums), reverse=True))))


def _cmp(a: str, b: str) -> int:
    if a + b > b + a:
        return -1          # a first
    if a + b < b + a:
        return 1
    return 0


def solve(nums: list[int]) -> str:
    parts = sorted(map(str, nums), key=cmp_to_key(_cmp))
    return "".join(parts).lstrip("0") or "0"


def main() -> None:
    for nums in ([10, 2], [3, 30, 34, 5, 9], [0, 0], [3, 30, 34], [121, 12], [7]):
        print(f"{str(nums):18} solve={solve(nums):10} brute={brute_force(nums):10} "
              f"lexicographic={wrong_lexicographic(nums)}")
    # functools.reduce folds a list left to right: ((1*2)*3)*4
    print("reduce product:", reduce(lambda acc, x: acc * x, [1, 2, 3, 4], 1))


if __name__ == "__main__":
    main()
