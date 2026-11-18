"""
Exercise 03 — Valid Anagram                              [Tier: ★ Core]
Chapter 09 · Pattern: frequency counting · Target time: 8 min

Problem
-------
Two strings are anagrams if one can be rearranged into the other, using every
character exactly once. Return True if s and t are anagrams (case-sensitive,
every character counts, including spaces).

Examples
--------
>>> solve("listen", "silent")
True
>>> solve("rat", "car")
False

Constraints
-----------
- 0 <= len(s), len(t) <= 10**5
- Arbitrary Unicode characters.

Hints
-----
- Different lengths -> cannot be anagrams.
- One dict: +1 for each char of s, -1 for each char of t; all counts must end at 0.
- sorted(s) == sorted(t) and Counter(s) == Counter(t) are valid one-liners.

Follow-ups
----------
- Only lowercase a-z? Use a fixed 26-slot list instead of a dict.
- Unicode normalisation ("é" as one code point vs e + combining accent)?
  Normalise with unicodedata.normalize("NFC", s) first.
- Streaming input that does not fit in memory: count chunk by chunk.
"""
from __future__ import annotations

from collections import Counter


def brute_force(s: str, t: str) -> bool:
    raise NotImplementedError("TODO")


def by_sorting(s: str, t: str) -> bool:
    raise NotImplementedError("TODO")


def by_counter(s: str, t: str) -> bool:
    raise NotImplementedError("TODO")


def solve(s: str, t: str) -> bool:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [("listen", "silent"), ("rat", "car"), ("", ""), ("a", "A"),
             ("aab", "abb"), ("dormitory", "dirtyroom")]
    for s, t in cases:
        results = {solve(s, t), brute_force(s, t), by_sorting(s, t), by_counter(s, t)}
        print(f"{s!r:<12} {t!r:<12} -> {solve(s, t)}  (all methods agree: {len(results) == 1})")


if __name__ == "__main__":
    main()
