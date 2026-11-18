"""
Exercise 07 — Combination sum II (each item once)  [Tier: ★ Core]
Chapter 18 · Pattern: backtracking + sort-and-skip dedup + early break · Target time: 15 min

Problem
-------
`candidates` may contain duplicates; each element may be used at most once. Return every distinct
combination (non-decreasing lists, in lexicographic order) whose sum equals `target`.

Examples
--------
>>> solve([10, 1, 2, 7, 6, 1, 5], 8)
[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]

Constraints
-----------
- 1 <= len(candidates) <= 100, 1 <= candidates[i] <= 50, 1 <= target <= 30

Hints
-----
- Combine Exercise 02 (skip equal siblings: `i > start and c[i] == c[i-1]`) with Exercise 06
  (break when the candidate exceeds the remainder).
- Recurse with i + 1 because each element is used once.

Approach ladder
---------------
1. Brute force — try all 2^n index subsets, keep those summing to target, dedupe sorted tuples.
   Hopeless at n = 100.
2. Optimal    — sort; backtrack with start index; skip equal siblings; break on overshoot.
   Duplicate subtrees and overshooting ranges are never entered.

Follow-ups
----------
- Return only the number of combinations (0/1 knapsack counting over distinct multisets is harder:
  group equal values and choose a count for each group).
- Combinations of exactly k numbers from 1..9 summing to n ("combination sum III").
"""
from __future__ import annotations


def brute_force(candidates: list[int], target: int) -> list[list[int]]:
    n = len(candidates)
    seen = set()
    for mask in range(1 << n):
        chosen = [candidates[i] for i in range(n) if mask >> i & 1]
        if sum(chosen) == target:
            seen.add(tuple(sorted(chosen)))
    return [list(t) for t in sorted(seen)]


def solve(candidates: list[int], target: int) -> list[list[int]]:
    candidates = sorted(candidates)
    result: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if i > start and c == candidates[i - 1]:
                continue                    # duplicate sibling -> identical subtree
            if c > remaining:
                break                       # sorted -> nothing later fits either
            path.append(c)
            backtrack(i + 1, remaining - c) # i + 1: each element at most once
            path.pop()

    backtrack(0, target)
    return result


def main() -> None:
    print("solve([10, 1, 2, 7, 6, 1, 5], 8) =", solve([10, 1, 2, 7, 6, 1, 5], 8))
    print("solve([2, 5, 2, 1, 2], 5)        =", solve([2, 5, 2, 1, 2], 5))
    print("solve([3], 2)                    =", solve([3], 2))
    data = [1, 1, 1, 2, 2, 3, 4, 5, 6, 6]
    print("agrees with brute force          :", solve(data, 9) == brute_force(data, 9))
    big = [1] * 60 + [2] * 40
    print("100 items (sixty 1s, forty 2s), target 10 ->", solve(big, 10))


if __name__ == "__main__":
    main()
