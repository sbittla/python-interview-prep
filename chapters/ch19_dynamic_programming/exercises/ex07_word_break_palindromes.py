"""
Exercise 07 — String DP: Word Break and Palindromes                 [Tier: ★ Core]
Chapter 19 · Pattern: prefix DP, interval-on-string DP · Target time: 40 min

Problem
-------
1. `word_break(s, words)` — can s be split into a sequence of dictionary words (each
   word reusable)? `word_break_split` returns one such split as a list, or None.
   The empty string splits into [] (True).
2. `count_pal_substrings(s)` — how many substrings (by position) are palindromes?
3. `lps(s)` — length of the longest palindromic SUBSEQUENCE of s (may skip characters).

Examples
--------
>>> word_break("applepenapple", {"apple", "pen"}), word_break("catsandog", {"cats", "dog", "sand", "and", "cat"})
(True, False)
>>> word_break_split("pineapplepen", {"apple", "pen", "pine", "pineapple"})
['pineapple', 'pen']
>>> count_pal_substrings("aaa"), lps("bbbab"), lps("cbbd")
(6, 4, 2)

Constraints
-----------
- 0 <= len(s) <= 1000; 1 <= len(words) <= 1000; each word has 1..20 characters.

Hints
-----
- Put the words in a set and limit the inner loop to the longest word length.
- Interval states must be filled shortest-first or i-descending; draw which cells a
  cell reads before choosing the loop order.

Follow-ups
----------
- Return ALL splits (word break II): backtracking plus this memo; output can be
  exponential in size.
- Minimum cuts to partition into palindromes: pal table + a 1D DP over prefixes.
"""
from __future__ import annotations

from functools import cache


# ---------------------------------------------------------------- word break
def word_break_brute(s: str, words: set[str]) -> bool:
    raise NotImplementedError("TODO")


def word_break_memo(s: str, words: set[str]) -> bool:
    raise NotImplementedError("TODO")


def _parents(s: str, words: set[str]) -> list[int | None]:
    raise NotImplementedError("TODO")


def word_break(s: str, words: set[str]) -> bool:
    raise NotImplementedError("TODO")


def word_break_split(s: str, words: set[str]) -> list[str] | None:
    raise NotImplementedError("TODO")


# ---------------------------------------------------------------- palindromic substrings
def count_pal_substrings_brute(s: str) -> int:
    raise NotImplementedError("TODO")


def count_pal_substrings_table(s: str) -> int:
    raise NotImplementedError("TODO")


def count_pal_substrings(s: str) -> int:
    raise NotImplementedError("TODO")


# ---------------------------------------------------------------- longest palindromic subsequence
def lps_brute(s: str) -> int:
    raise NotImplementedError("TODO")


def lps_memo(s: str) -> int:
    raise NotImplementedError("TODO")


def lps_table(s: str) -> int:
    raise NotImplementedError("TODO")


def lps(s: str) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    words = {"cats", "dog", "sand", "and", "cat"}
    for s in ("catsanddog", "catsandog", ""):
        print(f"word_break({s!r}) = {word_break(s, words)}  split = {word_break_split(s, words)}"
              f"  brute/memo = {word_break_brute(s, words)}/{word_break_memo(s, words)}")
    print("pineapplepen ->", word_break_split("pineapplepen", {"apple", "pen", "pine", "pineapple"}))
    nasty = "a" * 300 + "b"
    print("300 a's + 'b' with {a, aa, aaa}:", word_break(nasty, {"a", "aa", "aaa"}),
          "| memo:", word_break_memo(nasty, {"a", "aa", "aaa"}))
    for s in ("aaa", "abc", "abba", "racecar", ""):
        rungs = (count_pal_substrings_brute(s), count_pal_substrings_table(s), count_pal_substrings(s))
        print(f"palindromic substrings in {s!r}: {rungs[-1]}  rungs agree: {len(set(rungs)) == 1}")
    for s in ("bbbab", "cbbd", "character", "a", ""):
        rungs = (lps_brute(s), lps_memo(s), lps_table(s), lps(s))
        print(f"lps({s!r}) = {rungs[-1]}  rungs agree: {len(set(rungs)) == 1}")


if __name__ == "__main__":
    main()
