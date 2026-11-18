"""
Exercise 09 — Longest Palindromic Substring               [Tier: ◆ Extended]
Chapter 09 · Pattern: expand around centre · Target time: 25 min

Problem
-------
Return the longest contiguous substring of s that is a palindrome. If several
have the maximum length, return the one that starts first.

Examples
--------
>>> solve("babad")
'bab'
>>> solve("cbbd")
'bb'

Constraints
-----------
- 0 <= len(s) <= 1000

Approach ladder
---------------
1. Brute force — check all O(n^2) substrings, each check O(n): O(n^3).
2. Improved   — DP table pal[i][j] = s[i]==s[j] and pal[i+1][j-1]: O(n^2) time
   and O(n^2) space.
3. Optimal (for interviews) — expand around each of the 2n-1 centres (each
   character and each gap between characters). O(n^2) time, O(1) space, and far
   less code than the DP. (Manacher's algorithm is O(n) — mention, don't code.)

Follow-ups
----------
- Count all palindromic substrings: same expansion, add 1 per successful step.
- Longest palindromic *subsequence* is a different problem: DP (Chapter 19).
"""
from __future__ import annotations


def brute_force(s: str) -> str:
    best = ""
    n = len(s)
    for i in range(n):
        for j in range(i + 1, n + 1):
            sub = s[i:j]
            if len(sub) > len(best) and sub == sub[::-1]:
                best = sub
    return best


def dp_table(s: str) -> str:
    n = len(s)
    if n == 0:
        return ""
    pal = [[False] * n for _ in range(n)]
    start, length = 0, 1
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
                if j - i + 1 > length or (j - i + 1 == length and i < start):
                    start, length = i, j - i + 1
    return s[start:start + length]


def expand(s: str, lo: int, hi: int) -> tuple[int, int]:
    """Grow outwards while s[lo] == s[hi]; return the final [lo, hi) bounds."""
    while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
        lo -= 1
        hi += 1
    return lo + 1, hi


def solve(s: str) -> str:
    best_lo, best_hi = 0, 0
    for c in range(len(s)):
        for lo, hi in (expand(s, c, c), expand(s, c, c + 1)):   # odd, even
            if hi - lo > best_hi - best_lo:
                best_lo, best_hi = lo, hi
    return s[best_lo:best_hi]


def count_palindromes(s: str) -> int:
    total = 0
    for c in range(len(s)):
        for lo, hi in ((c, c), (c, c + 1)):
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                total += 1
                lo -= 1
                hi += 1
    return total


def main() -> None:
    for s in ["babad", "cbbd", "a", "", "forgeeksskeegfor", "abacdfgdcaba"]:
        print(f"{s!r:<20} -> {solve(s)!r:<14} brute={brute_force(s)!r} dp={dp_table(s)!r}")
    print("palindromic substrings in 'aaa':", count_palindromes("aaa"))


if __name__ == "__main__":
    main()
