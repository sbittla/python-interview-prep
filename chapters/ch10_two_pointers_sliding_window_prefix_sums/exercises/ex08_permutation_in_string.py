"""
Exercise 08 — Permutation in String / Anagram Windows    [Tier: ★ Core]
Chapter 10 · Pattern: fixed window + hash-map counts · Target time: 20 min

Problem
-------
solve(p, s): return True if some substring of s is a permutation of p
(same characters with the same multiplicities).
anagram_starts(p, s): return every start index i where s[i:i+len(p)] is a
permutation of p, in increasing order.

Examples
--------
>>> solve("ab", "eidbaooo"), solve("ab", "eidboaoo")
(True, False)
>>> anagram_starts("abc", "cbaebabacd")
[0, 6]

Constraints
-----------
- 1 <= len(p); 0 <= len(s) <= 10**5; any characters.

Hints
-----
- The window length is fixed at len(p); slide it and update counts by +1/-1.
- Track how many distinct characters currently have exactly the needed count.

Wrong-but-tempting
------------------
- Comparing set(window) == set(p): ignores multiplicities ("aab" vs "abb").
- Comparing Counters after `-=` without deleting zero counts: with a plain
  dict, {'a': 0, 'b': 1} != {'b': 1}. (collections.Counter equality ignores
  zero counts since Python 3.10; plain dicts never do.)

Follow-ups
----------
- Same idea for "find all anagrams" (anagram_starts) and for fixed-length
  windows with any count-based condition.
- Variable length with count constraints -> minimum window substring (ex09).
"""
from __future__ import annotations

from collections import Counter
from itertools import permutations


def brute_force(p: str, s: str) -> bool:
    raise NotImplementedError("TODO")


def sorted_windows(p: str, s: str) -> bool:
    raise NotImplementedError("TODO")


def wrong_set_compare(p: str, s: str) -> bool:
    """Wrong-but-tempting: compares character SETS, ignoring counts."""
    m = len(p)
    return any(set(s[i:i + m]) == set(p) for i in range(len(s) - m + 1))


def anagram_starts(p: str, s: str) -> list[int]:
    raise NotImplementedError("TODO")


def solve(p: str, s: str) -> bool:
    raise NotImplementedError("TODO")


def anagram_starts_brute(p: str, s: str) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [("ab", "eidbaooo"), ("ab", "eidboaoo"), ("abc", "cbaebabacd"), ("aab", "abbab"),
             ("a", ""), ("abc", "ab"), ("aa", "aaaa")]
    for p, s in cases:
        print(f"p={p!r:<6} s={s!r:<13} -> {solve(p, s)!s:<5} starts={anagram_starts(p, s)!s:<10}"
              f" brute={brute_force(p, s)!s:<5} set-compare(wrong)={wrong_set_compare(p, s)}")


if __name__ == "__main__":
    main()
