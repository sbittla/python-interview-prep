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

Approach ladder
---------------
1. Plain recursion — at index i, skip it or take it if it exceeds the last taken
   value: state (i, prev). O(2^n) time, O(n) stack.
2. Memoised on (i, prev) — O(n^2) states, O(1) each: O(n^2) time and space.
3. Bottom-up O(n^2) — recipe: state end(i) = LIS length ENDING at i; transition
   end(i) = 1 + max(end(j) for j < i with nums[j] < nums[i]) (or 1); base: none needed;
   order: i ascending; answer: max(end). A parent[] array rebuilds the sequence.
   O(n^2) time, O(n) space. Why move on: n = 10^5 means 10^10 steps.
4. Patience sorting — tails[k] = index of the smallest possible tail of an increasing
   subsequence of length k+1. tails values stay sorted, so each element finds its slot
   with bisect_left (strict increase; bisect_right would allow equal neighbours).
   Record parent = tails[k-1] at insertion time and walk back from tails[-1].
   O(n log n) time, O(n) space. Caution: the tails array itself is NOT an LIS.

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
    def best(i: int, prev: int) -> int:         # prev = index of last taken, -1 = none
        if i == len(nums):
            return 0
        skip = best(i + 1, prev)
        if prev < 0 or nums[i] > nums[prev]:
            return max(skip, 1 + best(i + 1, i))
        return skip

    return best(0, -1)


def lis_memo(nums: list[int]) -> int:
    @cache
    def best(i: int, prev: int) -> int:
        if i == len(nums):
            return 0
        skip = best(i + 1, prev)
        if prev < 0 or nums[i] > nums[prev]:
            return max(skip, 1 + best(i + 1, i))
        return skip

    return best(0, -1)


def lis_quadratic(nums: list[int]) -> list[int]:
    n = len(nums)
    if n == 0:
        return []
    end, parent = [1] * n, [-1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i] and end[j] + 1 > end[i]:
                end[i], parent[i] = end[j] + 1, j
    i = max(range(n), key=end.__getitem__)
    out = []
    while i != -1:
        out.append(nums[i])
        i = parent[i]
    return out[::-1]


def lis(nums: list[int]) -> list[int]:
    tails: list[int] = []                       # indices; nums[tails[k]] strictly increasing
    tail_vals: list[int] = []
    parent = [-1] * len(nums)
    for i, x in enumerate(nums):
        k = bisect_left(tail_vals, x)
        if k > 0:
            parent[i] = tails[k - 1]
        if k == len(tails):
            tails.append(i)
            tail_vals.append(x)
        else:
            tails[k], tail_vals[k] = i, x
    out, i = [], tails[-1] if tails else -1
    while i != -1:
        out.append(nums[i])
        i = parent[i]
    return out[::-1]


def lis_length(nums: list[int]) -> int:
    return len(lis(nums))


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
