"""
Exercise 11 — Character Toolbox: ord/chr, Counting, join     [Tier: ★ Core]
Chapter 06 · Pattern: strings as sequences · Target time: 15 min

Problem
-------
1. `first_unique(s)` — index of the first character that appears exactly once
   in `s`, or -1 if there is none.
2. `shift_letters(s, k)` — rotate each ASCII letter k places through the
   alphabet (wrapping, k may be negative or > 26), preserving case; every other
   character is unchanged. Build the result with `join`, not `+=`.
3. `letter_profile(s)` — a tuple of 26 ints: position i is how many times
   letter chr(ord('a') + i) appears in `s` (case-insensitive; other characters
   ignored). Two strings are letter-anagrams iff their profiles are equal, and
   the tuple is hashable, so it can key a dict of anagram groups.

Examples
--------
>>> first_unique("swiss")
1
>>> shift_letters("Hello, World!", 3)
'Khoor, Zruog!'
>>> letter_profile("Abba")[:3]
(2, 2, 0)

Constraints
-----------
- len(s) <= 10**5.

Hints
-----
- (ord(ch) - base + k) % 26 + base handles wrap-around and negative k.
- `str.isascii() and str.isalpha()` avoids shifting letters like 'é'.

Follow-ups
----------
- First unique in a STREAM: Counter plus an OrderedDict/deque of candidates.
- Unicode: `casefold()` and `unicodedata.normalize` before counting.
"""
from __future__ import annotations

import string
from collections import Counter


def brute_force_first_unique(s: str) -> int:
    raise NotImplementedError("TODO")


def first_unique(s: str) -> int:
    raise NotImplementedError("TODO")


def shift_letters(s: str, k: int) -> str:
    raise NotImplementedError("TODO")


def shift_with_translate(s: str, k: int) -> str:
    raise NotImplementedError("TODO")


def letter_profile(s: str) -> tuple[int, ...]:
    raise NotImplementedError("TODO")


def main() -> None:
    for s in ("swiss", "leetcode", "aabb", "", "z"):
        print(f"first_unique({s!r}) = {first_unique(s)}  brute = {brute_force_first_unique(s)}")
    for text, k in (("Hello, World!", 3), ("xyz ABC", 2), ("abc", -1), ("abc", 53), ("café", 1)):
        a, b = shift_letters(text, k), shift_with_translate(text, k)
        print(f"shift({text!r}, {k}) = {a!r}  translate agrees: {a == b}")
    print("profile('Abba')[:3] =", letter_profile("Abba")[:3], "| len =", len(letter_profile("Abba")))
    print("anagrams listen/silent:", letter_profile("listen") == letter_profile("silent"))
    print("ord('a') =", ord("a"), "| chr(90) =", chr(90), "| '-'.join('abc') =", "-".join("abc"))
    print("'a,b,,c'.split(',') =", "a,b,,c".split(","), "| ' a  b '.split() =", " a  b ".split())


if __name__ == "__main__":
    main()
