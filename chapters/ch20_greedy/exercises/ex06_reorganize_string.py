"""
Exercise 06 — Reorganise String                                    [Tier: ◆ Extended]
Chapter 20 · Pattern: greedy with a max-heap · Target time: 25 min

Problem
-------
Rearrange the characters of `s` so that no two adjacent characters are equal. Return any
valid arrangement, or "" if impossible. For determinism, break ties between equally frequent
characters alphabetically.

Examples
--------
>>> reorganize("aab")
'aba'
>>> reorganize("aaab")
''

Constraints
-----------
- 1 <= len(s) <= 500, lowercase letters.

Hints
-----
- When is it impossible? Compare the most frequent count with (n + 1) // 2.
- Using the most frequent letter first keeps the "danger" letter from piling up at the end.

Follow-ups
----------
- Rearrange so equal characters are at least k apart (generalise the cooldown queue).
- Count the number of valid arrangements: no longer greedy; inclusion-exclusion / DP.
"""
from __future__ import annotations

import heapq
from collections import Counter
from itertools import permutations


def is_valid(t: str) -> bool:
    raise NotImplementedError("TODO")


def brute_force(s: str) -> str:
    raise NotImplementedError("TODO")


def reorganize(s: str) -> str:
    raise NotImplementedError("TODO")


def reorganize_even_odd(s: str) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    for s in ("aab", "aaab", "aaabbc", "vvvlo", "a", "aa", "abcabc", "aaabb"):
        r = reorganize(s)
        e = reorganize_even_odd(s)
        print(f"{s!r:<9} heap={r!r:<9} valid={is_valid(r) if r else '-'!s:<5} "
              f"even/odd={e!r:<9} brute={brute_force(s)!r}")
    # Tempting but wrong: alternate in sorted order without counting frequencies
    s = "aaabc"
    naive = "".join(sorted(s))
    print("sorted naive for", repr(s), "->", repr(naive), "valid:", is_valid(naive),
          "| heap:", repr(reorganize(s)))


if __name__ == "__main__":
    main()
