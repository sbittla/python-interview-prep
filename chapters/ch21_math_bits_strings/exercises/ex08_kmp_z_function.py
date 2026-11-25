"""
Exercise 08 — KMP Prefix Function, Search, and the Z-function   [Tier: ★ Core (Z: ○)]
Chapter 21 · Pattern: border arrays for linear-time matching · Target time: 25 min

Problem
-------
1. ``prefix_function(s)``: pi[i] = length of the longest proper prefix of s[:i+1] that is
   also a suffix of it.
2. ``kmp_search(text, pattern)``: every start index where pattern occurs, overlaps included,
   ascending. An empty pattern matches at every index 0..len(text) (as ``str.find`` does).
3. ``smallest_repeating_unit(s)``: smallest p such that s == s[:p] * (len(s) // p), i.e. s is
   a whole repetition of s[:p] (len(s) if none; 0 for ""). Note: the shortest *period*
   n - pi[n-1] always exists ("abcab" -> 3); it is a repeating unit only when it divides n.
4. ○ ``z_function(s)``: z[i] = length of the longest common prefix of s and s[i:] (z[0] =
   len(s)); ``z_search(text, pattern)`` returns the same list as ``kmp_search``.

Examples
--------
>>> prefix_function("aabaaab")
[0, 1, 0, 1, 2, 2, 3]
>>> kmp_search("abababa", "aba")
[0, 2, 4]
>>> smallest_repeating_unit("abcabcabc"), smallest_repeating_unit("abcab")
(3, 5)
>>> z_function("aabxaab")
[7, 1, 0, 0, 3, 1, 0]

Constraints
-----------
- len(text), len(pattern) <= 10**5.

Hints
-----
- pi[i]: keep the current border length k; on a mismatch fall back with k = pi[k - 1].
- Search with the pattern's pi array; after a full match continue from pi[m - 1] so overlaps
  are found.
- The shortest period is p = n - pi[n - 1]; s is a whole repetition of s[:p] iff p divides n.
- Z: keep the window [l, r) of the rightmost prefix match; start z[i] at min(r - i, z[i - l]).

Wrong-but-tempting
------------------
- Resetting k to 0 on a mismatch: that is the brute force again.
- Resetting k to 0 after a match: misses overlapping occurrences.
- Returning n - pi[n - 1] without the divisibility check: "abcab" is not "abc" repeated.

Follow-ups
----------
- Repeated-substring pattern: s is a repetition iff smallest_repeating_unit(s) < len(s).
- Shortest palindrome by prepending: prefix_function(s + "#" + s[::-1]).
- Count distinct borders: follow pi[n-1], pi[pi[n-1]-1], ... down to 0.
"""
from __future__ import annotations


def prefix_function(s: str) -> list[int]:
    raise NotImplementedError("TODO")


def kmp_search(text: str, pattern: str) -> list[int]:
    raise NotImplementedError("TODO")


def brute_search(text: str, pattern: str) -> list[int]:
    raise NotImplementedError("TODO")


def find_all(text: str, pattern: str) -> list[int]:
    raise NotImplementedError("TODO")


def smallest_repeating_unit(s: str) -> int:
    raise NotImplementedError("TODO")


def z_function(s: str) -> list[int]:
    raise NotImplementedError("TODO")


def z_search(text: str, pattern: str) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    for s in ["aabaaab", "abcabd", "aaaa", "abacaba"]:
        print(f"pi({s!r:<10}) = {prefix_function(s)}   z = {z_function(s)}")
    for text, pat in [("abababa", "aba"), ("aaaaa", "aa"), ("hello", "xyz"), ("abc", ""), ("", "a")]:
        print(f"search({text!r}, {pat!r}): kmp={kmp_search(text, pat)} z={z_search(text, pat)} "
              f"find={find_all(text, pat)} brute={brute_search(text, pat)}")
    for s in ["abcabcabc", "abcab", "aaaa", "a", ""]:
        print(f"smallest_repeating_unit({s!r}) = {smallest_repeating_unit(s)}")


if __name__ == "__main__":
    main()
