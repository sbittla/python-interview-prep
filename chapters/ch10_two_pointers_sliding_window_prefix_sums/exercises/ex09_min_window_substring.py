"""
Exercise 09 — Minimum Window Containing All Required Characters  [Tier: ◆ Extended]
Chapter 10 · Pattern: variable-size sliding window (shortest valid) + counts · Target time: 30 min

Problem
-------
Given strings s and t, return the shortest substring of s that contains every
character of t with at least its multiplicity in t. If several shortest
windows exist, return the leftmost. Return "" if there is none or t is empty.

Examples
--------
>>> solve("ADOBECODEBANC", "ABC")
'BANC'
>>> solve("a", "aa")
''

Constraints
-----------
- 0 <= len(s), len(t) <= 10**5; case-sensitive; any characters.

Hints
-----
- Expand right until the window covers t; then shrink left while it still covers.
- Keep a single `missing` counter so the validity check is O(1).
- Only decrement `missing` when the entering character was still needed.

Wrong-but-tempting
------------------
- Comparing set(t) instead of counts: "AA" would accept a window with one A.
- Decrementing `missing` for every entering character that is in t, even
  when the window already has enough of it: it under-counts what's missing.

Follow-ups
----------
- Return the length only; or every minimum window.
- Smallest subarray with sum >= target (positive numbers): the same
  shrink-while-valid loop with a running sum.
"""
from __future__ import annotations

from collections import Counter


def _covers(window: Counter[str], need: Counter[str]) -> bool:
    return all(window[c] >= k for c, k in need.items())


def brute_force(s: str, t: str) -> str:
    raise NotImplementedError("TODO")


def extend_each_start(s: str, t: str) -> str:
    raise NotImplementedError("TODO")


def wrong_any_required(s: str, t: str) -> str:
    """Wrong-but-tempting: decrements `missing` even for surplus characters."""
    if not t:
        return ""
    need, have = Counter(t), Counter()
    missing, left, best = len(t), 0, (0, 0)
    for right, c in enumerate(s):
        have[c] += 1
        if c in need:
            missing -= 1                  # bug: ignores whether we already had enough
        while missing <= 0:
            if best == (0, 0) or right + 1 - left < best[1] - best[0]:
                best = (left, right + 1)
            d = s[left]
            have[d] -= 1
            if d in need:
                missing += 1
            left += 1
    return s[best[0]:best[1]]


def solve(s: str, t: str) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [("ADOBECODEBANC", "ABC"), ("a", "a"), ("a", "aa"), ("aa", "aa"), ("abc", ""),
             ("bbaac", "aba"), ("cabwefgewcwaefgcf", "cae")]
    for s, t in cases:
        print(f"s={s!r:<20} t={t!r:<6} -> {solve(s, t)!r:<7} brute={brute_force(s, t)!r:<7}"
              f" extend={extend_each_start(s, t)!r:<7} any-required(wrong)={wrong_any_required(s, t)!r}")


if __name__ == "__main__":
    main()
