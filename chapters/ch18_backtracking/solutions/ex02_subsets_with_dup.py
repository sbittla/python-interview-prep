"""
Exercise 02 — Subsets with duplicates              [Tier: ★ Core]
Chapter 18 · Pattern: backtracking + sort-and-skip dedup · Target time: 12 min

Problem
-------
The input list may contain repeated values. Return every distinct subset (as a multiset) exactly
once. Each subset is returned in non-decreasing order; the order of subsets does not matter.

Examples
--------
>>> sorted(solve([1, 2, 2]))
[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]

Constraints
-----------
- 0 <= len(nums) <= 12
- Values may repeat.

Hints
-----
- Sort first so equal values sit next to each other.
- At one level of the recursion, picking the first 2 or the second 2 leads to identical subtrees.
- Skip nums[i] when i > start and nums[i] == nums[i - 1].

Approach ladder
---------------
1. Brute force — generate all 2^n index subsets, convert each to a sorted tuple, dedupe with a set.
   O(n * 2^n) time and memory even when almost everything is a duplicate.
2. Optimal    — sort, then backtrack and skip equal siblings at the same depth. Duplicate subtrees
   are never entered, so the work is proportional to the number of distinct subsets.

Follow-ups
----------
- Why is the condition `i > start` and not `i > 0`? (Using the same value deeper is allowed.)
- Count distinct subsets without listing them: product of (count + 1) over distinct values.
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> list[list[int]]:
    n = len(nums)
    seen = {tuple(sorted(nums[i] for i in range(n) if mask >> i & 1)) for mask in range(1 << n)}
    return [list(t) for t in sorted(seen)]


def solve(nums: list[int]) -> list[list[int]]:
    nums = sorted(nums)
    result: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int) -> None:
        result.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue                    # same value already tried at this depth
            path.append(nums[i])
            backtrack(i + 1)
            path.pop()

    backtrack(0)
    return result


def main() -> None:
    print("solve([1, 2, 2])       =", solve([1, 2, 2]))
    print("brute_force([1, 2, 2]) =", brute_force([1, 2, 2]))
    print("agree                  :", sorted(solve([1, 2, 2])) == brute_force([1, 2, 2]))
    print("solve([2, 2, 2])       =", solve([2, 2, 2]))
    print("solve([4, 4, 1, 4])    =", solve([4, 4, 1, 4]))
    many = [1, 1, 2, 2, 3, 3, 3]
    print("distinct subsets of", many, "=", len(solve(many)), "(expected 3*3*4 = 36)")


if __name__ == "__main__":
    main()
