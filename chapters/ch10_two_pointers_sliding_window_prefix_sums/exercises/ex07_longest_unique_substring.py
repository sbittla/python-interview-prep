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

Hints
-----
- Grow right; while the new character is already in the window, shrink from the left.
- Each index enters and leaves the window at most once.

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
    raise NotImplementedError("TODO")


def extend_each_start(s: str) -> int:
    raise NotImplementedError("TODO")


def last_index_jump(s: str) -> int:
    raise NotImplementedError("TODO")


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
    raise NotImplementedError("TODO")


def best_substring(s: str) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    for s in ["abcabcbb", "bbbbb", "pwwkew", "", "abba", "dvdf", "tmmzuxt"]:
        print(f"s={s!r:<11} -> {solve(s)} {best_substring(s)!r:<8} brute={brute_force(s)}"
              f"  jump={last_index_jump(s)}  jump-without-max(wrong)={wrong_jump_without_max(s)}")


if __name__ == "__main__":
    main()
