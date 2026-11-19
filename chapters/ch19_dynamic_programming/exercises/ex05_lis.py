"""
Exercise 05 — Longest Increasing Subsequence with Reconstruction    [Tier: ★ Core]
Chapter 19 · Pattern: subsequence DP, patience sorting · Target time: 35 min

Problem
-------
A subsequence keeps elements in their original order but may skip any of them.
Return one longest STRICTLY increasing subsequence of nums (as a list of values).
`lis_length` returns only its length.

Examples
--------
>>> lis_length([10, 9, 2, 5, 3, 7, 101, 18])
4
>>> lis([10, 9, 2, 5, 3, 7, 101, 18])
[2, 3, 7, 18]
>>> lis([7, 7, 7]), lis([])
([7], [])

Constraints
-----------
- 0 <= len(nums) <= 10^5, values are integers (negative allowed).

Hints
-----
- end(i) is "ending at i", so the answer is a max over all i, not end(n-1).
- For patience sorting, store indices in tails so you can rebuild the answer.
- Non-decreasing variant: switch bisect_left to bisect_right.

Follow-ups
----------
- Number of longest increasing subsequences: carry a count beside end(i).
- Russian-doll envelopes: sort by width ascending, height descending, then LIS on height.
- LIS = LCS(nums, sorted(set(nums))) — correct but O(n^2).
"""
from __future__ import annotations

from bisect import bisect_left
from functools import cache


def lis_brute(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def lis_memo(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def lis_quadratic(nums: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def lis(nums: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def lis_length(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    for nums in ([10, 9, 2, 5, 3, 7, 101, 18], [0, 1, 0, 3, 2, 3], [7, 7, 7], [5, 4, 3],
                 [3, 1, 2, 1, 8, 5, 6], []):
        print(f"{str(nums):<28} len={lis_length(nums)}  lis={lis(nums)}  "
              f"O(n^2)={lis_quadratic(nums)}  brute/memo={lis_brute(nums)}/{lis_memo(nums)}")
    # patience trace: tails values after each element
    nums, tail_vals = [3, 1, 2, 1, 8, 5, 6], []
    for x in nums:
        k = bisect_left(tail_vals, x)
        tail_vals[k:k + 1] = [x]
        print(f"  after {x}: tails = {tail_vals}")
    tail_vals = []
    for x in [3, 4, 1]:
        tail_vals[bisect_left(tail_vals, x):bisect_left(tail_vals, x) + 1] = [x]
    print("[3, 4, 1]: tails =", tail_vals, "(not a subsequence!)  lis =", lis([3, 4, 1]))
    big = [(i * 7919) % 10007 for i in range(20000)]
    print("n=20000 pseudo-random LIS length:", lis_length(big))


if __name__ == "__main__":
    main()
