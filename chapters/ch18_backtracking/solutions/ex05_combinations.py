"""
Exercise 05 — Combinations (n choose k)            [Tier: ★ Core]
Chapter 18 · Pattern: backtracking with bound pruning · Target time: 10 min

Problem
-------
Return every way to choose k distinct numbers from 1..n, each as an increasing list, in
lexicographic order.

Examples
--------
>>> solve(4, 2)
[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]

Constraints
-----------
- 1 <= n <= 20, 0 <= k <= n

Hints
-----
- Same start-index template as subsets, but only record paths of length k.
- Prune: if the numbers left cannot fill the k - len(path) open slots, stop the loop early.

Approach ladder
---------------
1. Brute force — generate all 2^n subsets and keep those of size k. O(n * 2^n).
2. Improved   — backtracking that stops at depth k. Explores dead branches that run out of numbers.
3. Optimal    — the same with the bound `i <= n - (k - len(path)) + 1`, which removes every branch
   that cannot reach length k. Output-sensitive: O(k * C(n, k)).

Follow-ups
----------
- Return them lazily, or return only the m-th combination.
- Combination sum (Exercise 06) replaces the fixed size with a target sum.
"""
from __future__ import annotations


def brute_force(n: int, k: int) -> list[list[int]]:
    out = []
    for mask in range(1 << n):
        if bin(mask).count("1") == k:
            out.append([i + 1 for i in range(n) if mask >> i & 1])
    return sorted(out)


def solve(n: int, k: int, prune: bool = True, stats: dict | None = None) -> list[list[int]]:
    result: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int) -> None:
        if stats is not None:
            stats["calls"] = stats.get("calls", 0) + 1
        if len(path) == k:
            result.append(path[:])
            return
        last = n - (k - len(path)) + 1 if prune else n   # largest useful next value
        for i in range(start, last + 1):
            path.append(i)
            backtrack(i + 1)
            path.pop()

    backtrack(1)
    return result


def main() -> None:
    print("solve(4, 2)        =", solve(4, 2))
    print("matches brute force:", solve(4, 2) == brute_force(4, 2))
    print("solve(3, 3)        =", solve(3, 3))
    print("solve(3, 0)        =", solve(3, 0))
    for n, k in [(10, 5), (15, 12), (20, 18)]:
        a: dict = {}
        b: dict = {}
        solve(n, k, prune=False, stats=a)
        res = solve(n, k, prune=True, stats=b)
        print(f"n={n:2d} k={k:2d}: {len(res):5d} combos, calls without pruning={a['calls']:7d}, "
              f"with pruning={b['calls']:5d}")


if __name__ == "__main__":
    main()
