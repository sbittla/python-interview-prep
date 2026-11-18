"""
Exercise 03 — Palindrome After Normalisation                  [Tier: ★ Core]
Chapter 05 · Pattern: string slicing / two pointers · Target time: 10 min

Problem
-------
Decide whether a string reads the same forwards and backwards once you ignore every character
that is not a letter or digit and ignore letter case.

Examples
--------
>>> solve("A man, a plan, a canal: Panama")
True
>>> solve("race a car")
False
>>> solve("")
True

Constraints
-----------
- 0 <= len(s) <= 2 * 10**5; s may contain any Unicode characters

Approach ladder
---------------
1. Brute force — build the cleaned lowercase string with a generator expression and compare
   it with its reverse ``cleaned[::-1]``. O(n) time, O(n) extra space. Idiomatic and fast.
2. Optimal    — two indices walk inwards, skipping non-alphanumerics, comparing ``lower()``
   versions. O(n) time, O(1) extra space. Move up when the interviewer asks for no copies.

Follow-ups
----------
- Allow deleting at most one character (Valid Palindrome II): on the first mismatch, try
  skipping either side once.
- ``str.lower`` vs ``str.casefold``: casefold handles cases like German "ß" == "ss".
"""
from __future__ import annotations


def brute_force(s: str) -> bool:
    cleaned = "".join(ch.lower() for ch in s if ch.isalnum())
    return cleaned == cleaned[::-1]


def solve(s: str) -> bool:
    i, j = 0, len(s) - 1
    while i < j:
        if not s[i].isalnum():
            i += 1
        elif not s[j].isalnum():
            j -= 1
        elif s[i].lower() != s[j].lower():
            return False
        else:
            i, j = i + 1, j - 1
    return True


def main() -> None:
    cases = ["A man, a plan, a canal: Panama", "race a car", "", " ", ".,", "0P", "No 'x' in Nixon"]
    for s in cases:
        print(f"{s!r:36} -> {solve(s)!s:5}  brute agrees: {brute_force(s) == solve(s)}")


if __name__ == "__main__":
    main()
