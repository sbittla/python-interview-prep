"""
Exercise 08 — Palindrome partitioning              [Tier: ★ Core]
Chapter 18 · Pattern: backtracking over cut positions + precomputed table · Target time: 15 min

Problem
-------
Split string `s` into pieces so that every piece is a palindrome. Return all such splits, each as
a list of pieces, ordered by where the cuts fall (shorter first piece first).

Examples
--------
>>> solve("aab")
[['a', 'a', 'b'], ['aa', 'b']]

Constraints
-----------
- 1 <= len(s) <= 16, lowercase letters

Hints
-----
- The choice at each step is "where does the next piece end?" — try every end index.
- Only recurse when s[start:end+1] is a palindrome.
- Precompute is_pal[i][j] with DP (s[i] == s[j] and is_pal[i+1][j-1]) so each check is O(1).

Approach ladder
---------------
1. Brute force — try every one of the 2^(n-1) cut patterns, keep those whose pieces are all
   palindromes. O(n * 2^n).
2. Improved   — backtracking that only extends with palindromic pieces; palindrome check by slicing
   costs O(n) per check.
3. Optimal    — the same backtracking with an O(n^2) precomputed palindrome table; each check O(1).
   Output can still be 2^(n-1) partitions (all 'a's), so the worst case remains exponential.

Follow-ups
----------
- Minimum number of cuts (Chapter 19 — that is DP, not backtracking).
- Count the partitions without listing them (DP over prefixes).
"""
from __future__ import annotations


def _is_palindrome(t: str) -> bool:
    return t == t[::-1]


def brute_force(s: str) -> list[list[str]]:
    n = len(s)
    result = []
    for mask in range(1 << (n - 1)):        # bit i set = cut after position i
        pieces, start = [], 0
        for i in range(n - 1):
            if mask >> i & 1:
                pieces.append(s[start:i + 1])
                start = i + 1
        pieces.append(s[start:])
        if all(_is_palindrome(p) for p in pieces):
            result.append(pieces)
    return sorted(result, key=lambda ps: [len(p) for p in ps])


def solve(s: str) -> list[list[str]]:
    n = len(s)
    is_pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):          # i descends so is_pal[i+1] is ready
        for j in range(i, n):
            is_pal[i][j] = s[i] == s[j] and (j - i < 2 or is_pal[i + 1][j - 1])

    result: list[list[str]] = []
    path: list[str] = []

    def backtrack(start: int) -> None:
        if start == n:
            result.append(path[:])
            return
        for end in range(start, n):
            if is_pal[start][end]:
                path.append(s[start:end + 1])
                backtrack(end + 1)
                path.pop()

    backtrack(0)
    return result


def main() -> None:
    print("solve('aab')   =", solve("aab"))
    print("solve('a')     =", solve("a"))
    print("solve('racecar') =", solve("racecar"))
    print("solve('abba')  =", solve("abba"))
    print("brute agrees on 'aabbaa':",
          sorted(solve("aabbaa")) == sorted(brute_force("aabbaa")))
    print("partitions of 'a'*10 =", len(solve("a" * 10)), "(2^9 = 512)")


if __name__ == "__main__":
    main()
