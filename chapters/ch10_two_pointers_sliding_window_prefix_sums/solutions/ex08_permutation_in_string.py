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

Approach ladder
---------------
1. Brute force — generate every permutation of p and search for it.
   O(m! * n * m) — only for tiny p, but a useful oracle.
2. Improved   — for each window of length m, compare sorted(window) with
   sorted(p): O(n * m log m). Or build Counter(window) from scratch per
   window: O(n * m).
3. Optimal    — slide a fixed window of length m and update one Counter
   incrementally (+1 entering, -1 leaving), comparing counts each step.
   Tracking `matched` (how many distinct characters currently have the right
   count) makes each step O(1): O(n + m) time, O(sigma) space.

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
    return any("".join(perm) in s for perm in set(permutations(p)))


def sorted_windows(p: str, s: str) -> bool:
    m, key = len(p), sorted(p)
    return any(sorted(s[i:i + m]) == key for i in range(len(s) - m + 1))


def wrong_set_compare(p: str, s: str) -> bool:
    """Wrong-but-tempting: compares character SETS, ignoring counts."""
    m = len(p)
    return any(set(s[i:i + m]) == set(p) for i in range(len(s) - m + 1))


def anagram_starts(p: str, s: str) -> list[int]:
    m = len(p)
    need = Counter(p)
    have: Counter[str] = Counter()
    matched = 0                           # distinct chars with have[c] == need[c]
    out = []
    for right, c in enumerate(s):
        if c in need:                     # c enters
            have[c] += 1
            if have[c] == need[c]:
                matched += 1
            elif have[c] == need[c] + 1:
                matched -= 1              # was matched, now one too many
        if right >= m and s[right - m] in need:
            d = s[right - m]              # d leaves
            have[d] -= 1
            if have[d] == need[d]:
                matched += 1
            elif have[d] == need[d] - 1:
                matched -= 1              # was matched, now one too few
        if right >= m - 1 and matched == len(need):
            out.append(right - m + 1)
    return out


def solve(p: str, s: str) -> bool:
    return bool(anagram_starts(p, s))


def anagram_starts_brute(p: str, s: str) -> list[int]:
    m, key = len(p), Counter(p)
    return [i for i in range(len(s) - m + 1) if Counter(s[i:i + m]) == key]


def main() -> None:
    cases = [("ab", "eidbaooo"), ("ab", "eidboaoo"), ("abc", "cbaebabacd"), ("aab", "abbab"),
             ("a", ""), ("abc", "ab"), ("aa", "aaaa")]
    for p, s in cases:
        print(f"p={p!r:<6} s={s!r:<13} -> {solve(p, s)!s:<5} starts={anagram_starts(p, s)!s:<10}"
              f" brute={brute_force(p, s)!s:<5} set-compare(wrong)={wrong_set_compare(p, s)}")


if __name__ == "__main__":
    main()
