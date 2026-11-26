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

Hints
-----
1. ``brute_force``: build a cleaned, lower-cased copy and compare it with its reverse.
2. ``solve``: can you avoid the copy? Think of two indices that move towards each other and
   what each one should do with characters that do not count.
3. Check ``""``, a string of only punctuation, and ``"0P"``.

Follow-ups
----------
- Allow deleting at most one character (Valid Palindrome II).
- ``str.lower`` vs ``str.casefold``: when do they differ?
"""
from __future__ import annotations


def brute_force(s: str) -> bool:
    raise NotImplementedError("TODO")


def solve(s: str) -> bool:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = ["A man, a plan, a canal: Panama", "race a car", "", " ", ".,", "0P", "No 'x' in Nixon"]
    for s in cases:
        print(f"{s!r:36} -> {solve(s)!s:5}  brute agrees: {brute_force(s) == solve(s)}")


if __name__ == "__main__":
    main()
