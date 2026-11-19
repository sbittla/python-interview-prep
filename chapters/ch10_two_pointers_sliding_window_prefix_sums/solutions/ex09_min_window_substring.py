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

Approach ladder
---------------
1. Brute force — test every substring with a Counter "covers" check, keep the
   shortest. O(n^2 * (n + m)) time.
2. Improved   — for each left end, extend right until the window covers t
   (incremental counts), then stop: the first cover from each start is that
   start's shortest. O(n^2) time — still restarts from scratch per start.
3. Optimal    — one window. Expand right until valid; then shrink left while
   still valid, recording the best each time; the first shrink that breaks
   validity hands control back to the expand step. `missing` = how many
   required characters (with multiplicity) the window still lacks, so the
   validity test is O(1). Each index enters and leaves once: O(n + m) time,
   O(sigma) space.

Window invariant: when the inner loop runs, s[left:right+1] covers t; the
answer for every right end is the window at the moment just before
validity breaks. Validity is monotone (a super-window of a covering window
also covers), which is why shrinking-while-valid finds the shortest.

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
    if not t:
        return ""
    need, best = Counter(t), ""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if (not best or j - i < len(best)) and _covers(Counter(s[i:j]), need):
                best = s[i:j]
    return best


def extend_each_start(s: str, t: str) -> str:
    if not t:
        return ""
    need, best = Counter(t), ""
    for i in range(len(s)):
        missing, have = len(t), Counter()
        for j in range(i, len(s)):
            c = s[j]
            have[c] += 1
            if have[c] <= need[c]:
                missing -= 1
            if missing == 0:
                if not best or j - i + 1 < len(best):
                    best = s[i:j + 1]
                break
    return best


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
    if not t:
        return ""
    need = Counter(t)
    missing = len(t)                      # required chars still absent
    left, best_len, best_start = 0, len(s) + 1, 0
    for right, c in enumerate(s):
        if need[c] > 0:
            missing -= 1                  # c was still needed
        need[c] -= 1                      # negative = surplus in window
        while missing == 0:               # valid: try to shrink
            if right - left + 1 < best_len:
                best_len, best_start = right - left + 1, left
            d = s[left]
            need[d] += 1
            if need[d] > 0:
                missing += 1              # removing d broke validity
            left += 1
    return "" if best_len > len(s) else s[best_start:best_start + best_len]


def main() -> None:
    cases = [("ADOBECODEBANC", "ABC"), ("a", "a"), ("a", "aa"), ("aa", "aa"), ("abc", ""),
             ("bbaac", "aba"), ("cabwefgewcwaefgcf", "cae")]
    for s, t in cases:
        print(f"s={s!r:<20} t={t!r:<6} -> {solve(s, t)!r:<7} brute={brute_force(s, t)!r:<7}"
              f" extend={extend_each_start(s, t)!r:<7} any-required(wrong)={wrong_any_required(s, t)!r}")


if __name__ == "__main__":
    main()
