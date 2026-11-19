"""
Exercise 07 — Longest Substring Without Repeats          [Tier: ★ Core]
Chapter 10 · Pattern: variable-size sliding window (longest valid) · Target time: 20 min

Problem
-------
Return the length of the longest substring of s in which no character occurs
twice. best_substring(s) returns the leftmost such substring itself.

Examples
--------
>>> solve("abcabcbb"), best_substring("abcabcbb")
(3, 'abc')
>>> solve("pwwkew"), best_substring("pwwkew")
(3, 'wke')
>>> solve("")
0

Constraints
-----------
- 0 <= len(s) <= 5 * 10**4; any Unicode characters.

Approach ladder
---------------
1. Brute force — check every substring with len(set(sub)) == len(sub).
   O(n^3) time (n^2 substrings, O(n) check each).
2. Improved   — for each start, extend right while characters are new; stop
   at the first repeat. O(n * min(n, sigma)) time; still quadratic for large
   alphabets. Wasteful because after a repeat we restart from scratch.
3. Optimal    — one window [left, right]. Add s[right]; while it is a
   duplicate, remove s[left] and advance left. Each index enters and leaves
   once: O(n) time, O(min(n, sigma)) space.
   Variant: store last-seen index and jump left = max(left, last[c] + 1) in
   O(1) per step (same O(n), fewer operations).

Window invariant: s[left:right+1] has no repeated character after the
shrink loop; validity is monotone (a sub-window of a valid window is valid),
which is exactly why shrinking from the left is safe.

Wrong-but-tempting
------------------
- Jump version written as left = last[c] + 1 without max(): left can move
  BACKWARDS to a stale position ("abba" gives 3 instead of 2).

Follow-ups
----------
- At most k distinct characters: same template, a Counter, shrink while
  len(counter) > k.
- Longest substring where you may replace up to k characters: shrink while
  window_len - max_count > k.
"""
from __future__ import annotations


def brute_force(s: str) -> int:
    best = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if len(set(s[i:j])) == j - i:
                best = max(best, j - i)
    return best


def extend_each_start(s: str) -> int:
    best = 0
    for i in range(len(s)):
        seen: set[str] = set()
        for c in s[i:]:
            if c in seen:
                break
            seen.add(c)
        best = max(best, len(seen))
    return best


def last_index_jump(s: str) -> int:
    last: dict[str, int] = {}
    left = best = 0
    for right, c in enumerate(s):
        if c in last:
            left = max(left, last[c] + 1)   # never move left backwards
        last[c] = right
        best = max(best, right - left + 1)
    return best


def wrong_jump_without_max(s: str) -> int:
    """Wrong-but-tempting: lets left move backwards to a stale index."""
    last: dict[str, int] = {}
    left = best = 0
    for right, c in enumerate(s):
        if c in last:
            left = last[c] + 1
        last[c] = right
        best = max(best, right - left + 1)
    return best


def solve(s: str) -> int:
    window: set[str] = set()
    left = best = 0
    for right, c in enumerate(s):
        while c in window:                # shrink until valid again
            window.remove(s[left])
            left += 1
        window.add(c)
        best = max(best, right - left + 1)
    return best


def best_substring(s: str) -> str:
    window: set[str] = set()
    left = start = length = 0
    for right, c in enumerate(s):
        while c in window:
            window.remove(s[left])
            left += 1
        window.add(c)
        if right - left + 1 > length:     # strict: keep the leftmost
            start, length = left, right - left + 1
    return s[start:start + length]


def main() -> None:
    for s in ["abcabcbb", "bbbbb", "pwwkew", "", "abba", "dvdf", "tmmzuxt"]:
        print(f"s={s!r:<11} -> {solve(s)} {best_substring(s)!r:<8} brute={brute_force(s)}"
              f"  jump={last_index_jump(s)}  jump-without-max(wrong)={wrong_jump_without_max(s)}")


if __name__ == "__main__":
    main()
