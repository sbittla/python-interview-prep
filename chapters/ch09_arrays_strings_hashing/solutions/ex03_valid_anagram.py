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

Approach ladder
---------------
1. Brute force — for each char of s, find and remove one occurrence from a list
   copy of t. O(n^2) time.
2. Improved   — sorted(s) == sorted(t). O(n log n) time, O(n) space. Often fine!
3. Optimal    — count characters in one dict: +1 for s, -1 for t, all zero at
   the end. O(n) time, O(k) space for k distinct characters. Early exit when the
   lengths differ.

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
    if len(s) != len(t):
        return False
    pool = list(t)
    for ch in s:
        if ch not in pool:
            return False
        pool.remove(ch)          # O(n) each -> O(n^2)
    return True


def by_sorting(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)


def by_counter(s: str, t: str) -> bool:
    return Counter(s) == Counter(t)


def solve(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    balance: dict[str, int] = {}
    for a, b in zip(s, t):
        balance[a] = balance.get(a, 0) + 1
        balance[b] = balance.get(b, 0) - 1
    return all(v == 0 for v in balance.values())


def main() -> None:
    cases = [("listen", "silent"), ("rat", "car"), ("", ""), ("a", "A"),
             ("aab", "abb"), ("dormitory", "dirtyroom")]
    for s, t in cases:
        results = {solve(s, t), brute_force(s, t), by_sorting(s, t), by_counter(s, t)}
        print(f"{s!r:<12} {t!r:<12} -> {solve(s, t)}  (all methods agree: {len(results) == 1})")


if __name__ == "__main__":
    main()
