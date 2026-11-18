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

Approach ladder
---------------
1. Brute force — build the cleaned string, compare with its reverse
   cleaned == cleaned[::-1]. O(n) time, O(n) extra space. Perfectly fine in
   Python and often the best first answer.
2. Optimal    — two pointers from both ends, skipping non-alphanumerics,
   comparing lower-cased chars. O(n) time, O(1) extra space.
   Move up only when the interviewer asks for O(1) space.
3. One-delete variant — on the first mismatch, try skipping the left OR the
   right char and check the remaining range. O(n) total.

Follow-ups
----------
- At most k deletions -> DP on the longest palindromic subsequence (Ch19).
- Unicode letters: str.isalnum() already accepts them; str.casefold() is the
  more aggressive lower-casing ("ß" -> "ss").
"""
from __future__ import annotations


def brute_force(s: str) -> bool:
    cleaned = [ch.lower() for ch in s if ch.isalnum()]
    return cleaned == cleaned[::-1]


def solve(s: str) -> bool:
    lo, hi = 0, len(s) - 1
    while lo < hi:
        if not s[lo].isalnum():
            lo += 1
        elif not s[hi].isalnum():
            hi -= 1
        elif s[lo].lower() != s[hi].lower():
            return False
        else:
            lo += 1
            hi -= 1
    return True


def _is_pal(s: str, lo: int, hi: int) -> bool:
    while lo < hi:
        if s[lo] != s[hi]:
            return False
        lo += 1
        hi -= 1
    return True


def solve_one_delete(s: str) -> bool:
    lo, hi = 0, len(s) - 1
    while lo < hi:
        if s[lo] != s[hi]:
            return _is_pal(s, lo + 1, hi) or _is_pal(s, lo, hi - 1)
        lo += 1
        hi -= 1
    return True


def main() -> None:
    for s in ["A man, a plan, a canal: Panama", "race a car", "", " ", ".,", "0P", "No 'x' in Nixon"]:
        print(f"{s!r:<34} palindrome={solve(s)}  brute={brute_force(s)}")
    for s in ["abca", "abc", "deeee", "a", "cbbcc"]:
        print(f"one-delete {s!r:<8} -> {solve_one_delete(s)}")


if __name__ == "__main__":
    main()
