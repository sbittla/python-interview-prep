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

Hints
-----
- Every palindrome has a centre: a character (odd length) or a gap (even length).
- expand(s, lo, hi) grows while s[lo] == s[hi] and returns the final [lo, hi) bounds.
- Try 2n - 1 centres; keep the longest (strictly longer keeps the earliest start).

Follow-ups
----------
- Count all palindromic substrings: same expansion, add 1 per successful step.
- Longest palindromic *subsequence* is a different problem: DP (Chapter 19).
"""
from __future__ import annotations


def brute_force(s: str) -> str:
    raise NotImplementedError("TODO")


def dp_table(s: str) -> str:
    raise NotImplementedError("TODO")


def expand(s: str, lo: int, hi: int) -> tuple[int, int]:
    """Grow outwards while s[lo] == s[hi]; return the final [lo, hi) bounds."""
    raise NotImplementedError("TODO")


def solve(s: str) -> str:
    raise NotImplementedError("TODO")


def count_palindromes(s: str) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    for s in ["babad", "cbbd", "a", "", "forgeeksskeegfor", "abacdfgdcaba"]:
        print(f"{s!r:<20} -> {solve(s)!r:<14} brute={brute_force(s)!r} dp={dp_table(s)!r}")
    print("palindromic substrings in 'aaa':", count_palindromes("aaa"))


if __name__ == "__main__":
    main()
