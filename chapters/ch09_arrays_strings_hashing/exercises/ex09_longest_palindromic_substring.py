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
- Every palindrome is symmetric about a middle. Where can that middle be?
- How many possible middles does a string of length n have?
- Ties: the earliest start wins. Which comparison keeps that?

Follow-ups
----------
- Count all palindromic substrings (count_palindromes).
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
