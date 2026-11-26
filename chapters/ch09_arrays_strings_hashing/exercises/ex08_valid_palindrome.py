"""
Exercise 08 — Valid Palindrome (alphanumeric, ignore case) [Tier: ★ Core]
Chapter 09 · Pattern: string two-pointer scan · Target time: 10 min

Problem
-------
A phrase is a palindrome if, after lower-casing it and keeping only letters and
digits, it reads the same forwards and backwards. Return True if s is one.
Also implement solve_one_delete(s): True if s (taken literally, no filtering)
can become a palindrome by deleting at most one character.

Examples
--------
>>> solve("A man, a plan, a canal: Panama")
True
>>> solve("race a car")
False
>>> solve_one_delete("abca")
True

Constraints
-----------
- 0 <= len(s) <= 2 * 10**5

Hints
-----
- The reversed-copy check is a fine first answer; what does it cost in space?
- Can you compare characters from both ends without building a copy?
- One-delete: at the first mismatch, how many candidate deletions are there?

Follow-ups
----------
- At most k deletions -> DP on the longest palindromic subsequence (Ch19).
- Unicode letters: str.isalnum() already accepts them; str.casefold() is the
  more aggressive lower-casing ("ß" -> "ss").
"""
from __future__ import annotations


def brute_force(s: str) -> bool:
    raise NotImplementedError("TODO")


def solve(s: str) -> bool:
    raise NotImplementedError("TODO")


def _is_pal(s: str, lo: int, hi: int) -> bool:
    raise NotImplementedError("TODO")


def solve_one_delete(s: str) -> bool:
    raise NotImplementedError("TODO")


def main() -> None:
    for s in ["A man, a plan, a canal: Panama", "race a car", "", " ", ".,", "0P", "No 'x' in Nixon"]:
        print(f"{s!r:<34} palindrome={solve(s)}  brute={brute_force(s)}")
    for s in ["abca", "abc", "deeee", "a", "cbbcc"]:
        print(f"one-delete {s!r:<8} -> {solve_one_delete(s)}")


if __name__ == "__main__":
    main()
