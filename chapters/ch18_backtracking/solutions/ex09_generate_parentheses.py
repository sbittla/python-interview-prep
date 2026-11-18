"""
Exercise 09 — Generate parentheses                 [Tier: ★ Core]
Chapter 18 · Pattern: backtracking with validity counters · Target time: 10 min

Problem
-------
Return every string of n pairs of balanced parentheses, in lexicographic order ('(' < ')').

Examples
--------
>>> solve(3)
['((()))', '(()())', '(())()', '()(())', '()()()']

Constraints
-----------
- 1 <= n <= 10

Hints
-----
- You never need to check a whole string: keep two counters, opened and closed.
- You may add '(' while opened < n, and ')' while closed < opened.
- The number of answers is the n-th Catalan number: 1, 2, 5, 14, 42, ...

Approach ladder
---------------
1. Brute force — generate all 2^(2n) strings of '(' and ')' and keep the balanced ones.
   O(n * 4^n).
2. Optimal    — build left to right, only making moves that keep the prefix valid. Every leaf is an
   answer, so the work is O(n * C_n) where C_n ~ 4^n / (n^1.5 * sqrt(pi)).

Follow-ups
----------
- Remove the minimum number of parentheses to make a string valid (BFS or two-pass greedy).
- Several bracket types: then you need a stack instead of counters.
"""
from __future__ import annotations

from itertools import product


def _balanced(t: str) -> bool:
    depth = 0
    for ch in t:
        depth += 1 if ch == "(" else -1
        if depth < 0:
            return False
    return depth == 0


def brute_force(n: int) -> list[str]:
    return [t for t in ("".join(p) for p in product("()", repeat=2 * n)) if _balanced(t)]


def solve(n: int) -> list[str]:
    result: list[str] = []
    path: list[str] = []

    def backtrack(opened: int, closed: int) -> None:
        if len(path) == 2 * n:
            result.append("".join(path))
            return
        if opened < n:                      # may still open
            path.append("(")
            backtrack(opened + 1, closed)
            path.pop()
        if closed < opened:                 # may close only what is open
            path.append(")")
            backtrack(opened, closed + 1)
            path.pop()

    backtrack(0, 0)
    return result


def main() -> None:
    print("solve(1) =", solve(1))
    print("solve(2) =", solve(2))
    print("solve(3) =", solve(3))
    print("brute force agrees for n=1..6:", all(solve(n) == brute_force(n) for n in range(1, 7)))
    print("Catalan counts n=1..10:", [len(solve(n)) for n in range(1, 11)])


if __name__ == "__main__":
    main()
