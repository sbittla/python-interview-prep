"""
Exercise 06 — Combination sum (reuse allowed)      [Tier: ★ Core]
Chapter 18 · Pattern: backtracking + sorted early break · Target time: 15 min

Problem
-------
Given distinct positive integers `candidates` and a positive `target`, return every multiset of
candidates (each candidate may be used any number of times) whose sum is exactly `target`.
Each combination is listed in non-decreasing order; combinations are in lexicographic order.

Examples
--------
>>> solve([2, 3, 6, 7], 7)
[[2, 2, 3], [7]]
>>> solve([2], 1)
[]

Constraints
-----------
- 1 <= len(candidates) <= 30, all distinct, 2 <= candidates[i] <= 40
- 1 <= target <= 40

Hints
-----
- To allow reuse, recurse with the SAME index i (not i + 1) after choosing candidates[i].
- To avoid [2, 3, 2] and [2, 2, 3] both appearing, never go back to an earlier index.
- Sort the candidates; once one is larger than the remaining target, all later ones are too: break.

Approach ladder
---------------
1. Brute force — include/exclude recursion on index i ("take i again" or "move to i + 1"),
   no sorting, no pruning: explores every branch until the remainder goes negative.
2. Optimal    — sorted candidates, start-index loop, `break` as soon as a candidate exceeds the
   remainder. Worst case still exponential (about O(N^(T/m)) where m is the smallest candidate),
   but the break cuts whole sibling ranges, not just one branch.

Follow-ups
----------
- Each candidate used at most once and duplicates in the input (Exercise 07).
- Only count the combinations: that is unbounded-knapsack DP (Chapter 19, coin change II).
"""
from __future__ import annotations


def brute_force(candidates: list[int], target: int) -> list[list[int]]:
    result: list[list[int]] = []
    path: list[int] = []

    def go(i: int, remaining: int) -> None:
        if remaining == 0:
            result.append(sorted(path))
            return
        if remaining < 0 or i == len(candidates):
            return
        path.append(candidates[i])          # take candidates[i] (and maybe again)
        go(i, remaining - candidates[i])
        path.pop()
        go(i + 1, remaining)                # skip to the next candidate

    go(0, target)
    return sorted(result)


def solve(candidates: list[int], target: int, stats: dict | None = None) -> list[list[int]]:
    candidates = sorted(candidates)
    result: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if stats is not None:
            stats["calls"] = stats.get("calls", 0) + 1
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break                       # sorted: every later candidate is too big as well
            path.append(c)
            backtrack(i, remaining - c)     # i, not i + 1: reuse allowed
            path.pop()

    backtrack(0, target)
    return result


def main() -> None:
    print("solve([2, 3, 6, 7], 7) =", solve([2, 3, 6, 7], 7))
    print("solve([2, 3, 5], 8)    =", solve([2, 3, 5], 8))
    print("solve([2], 1)          =", solve([2], 1))
    print("solve([7, 3, 2], 18)   has", len(solve([7, 3, 2], 18)), "combinations")
    print("agrees with brute force:", solve([7, 3, 2], 18) == brute_force([7, 3, 2], 18))
    stats: dict = {}
    solve([2, 3, 5, 7, 11, 13], 30, stats=stats)
    print("calls for target 30 over 6 primes:", stats["calls"])


if __name__ == "__main__":
    main()
