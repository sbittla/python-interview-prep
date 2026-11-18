"""
Exercise 04 — Permutations with duplicates         [Tier: ★ Core]
Chapter 18 · Pattern: backtracking + dedup (sorted skip or Counter) · Target time: 15 min

Problem
-------
The input may contain repeated values. Return every distinct ordering exactly once, in
lexicographic order.

Examples
--------
>>> solve([1, 1, 2])
[[1, 1, 2], [1, 2, 1], [2, 1, 1]]

Constraints
-----------
- 0 <= len(nums) <= 8

Hints
-----
- Sort. Equal values must be placed in a fixed relative order, so swapping two equal values never
  produces a "new" permutation.
- Skip index i when nums[i] == nums[i-1] and nums[i-1] is NOT currently used.
- Alternative: recurse over a Counter of remaining values — each distinct value is tried once
  per level.

Approach ladder
---------------
1. Brute force — generate all n! permutations and dedupe with a set: wasted work when many repeat.
2. Optimal    — sorted + "previous equal value unused" skip, or a Counter of remaining values.
   Work is proportional to (number of distinct permutations) * n.

Follow-ups
----------
- Why does `not used[i-1]` work? (It forces equal values to be used left to right.)
- Count distinct permutations directly: n! / (c1! * c2! * ...).
"""
from __future__ import annotations

from collections import Counter
from itertools import permutations


def brute_force(nums: list[int]) -> list[list[int]]:
    return [list(p) for p in sorted(set(permutations(nums)))]


def solve(nums: list[int]) -> list[list[int]]:
    nums = sorted(nums)
    result: list[list[int]] = []
    path: list[int] = []
    used = [False] * len(nums)

    def backtrack() -> None:
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue                    # equal values are taken left to right only
            used[i] = True
            path.append(nums[i])
            backtrack()
            path.pop()
            used[i] = False

    backtrack()
    return result


def solve_counter(nums: list[int]) -> list[list[int]]:
    counts = Counter(nums)
    keys = sorted(counts)
    result: list[list[int]] = []
    path: list[int] = []

    def backtrack() -> None:
        if len(path) == len(nums):
            result.append(path[:])
            return
        for x in keys:                      # each distinct value once per level
            if counts[x] == 0:
                continue
            counts[x] -= 1
            path.append(x)
            backtrack()
            path.pop()
            counts[x] += 1

    backtrack()
    return result


def main() -> None:
    print("solve([1, 1, 2])         =", solve([1, 1, 2]))
    print("solve_counter([1, 1, 2]) =", solve_counter([1, 1, 2]))
    print("brute_force([1, 1, 2])   =", brute_force([1, 1, 2]))
    data = [1, 1, 2, 2, 3]
    print("distinct perms of", data, "=", len(solve(data)), "(5!/(2!2!1!) = 30)")
    print("all three agree          :", solve(data) == solve_counter(data) == brute_force(data))
    print("solve([7, 7, 7])         =", solve([7, 7, 7]))


if __name__ == "__main__":
    main()
