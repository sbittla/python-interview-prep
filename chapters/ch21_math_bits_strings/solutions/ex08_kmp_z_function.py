"""
Exercise 08 — KMP Prefix Function, Search, and the Z-function   [Tier: ★ Core (Z: ○)]
Chapter 21 · Pattern: border arrays for linear-time matching · Target time: 25 min

Problem
-------
1. ``prefix_function(s)``: pi[i] = length of the longest proper prefix of s[:i+1] that is
   also a suffix of it.
2. ``kmp_search(text, pattern)``: every start index where pattern occurs, overlaps included,
   ascending. An empty pattern matches at every index 0..len(text) (as ``str.find`` does).
3. ``shortest_period(s)``: smallest p such that s is a repetition of s[:p] (len(s) if none).
4. ○ ``z_function(s)``: z[i] = length of the longest common prefix of s and s[i:] (z[0] =
   len(s)); ``z_search(text, pattern)`` returns the same list as ``kmp_search``.

Examples
--------
>>> prefix_function("aabaaab")
[0, 1, 0, 1, 2, 2, 3]
>>> kmp_search("abababa", "aba")
[0, 2, 4]
>>> shortest_period("abcabcabc"), shortest_period("abcab")
(3, 5)
>>> z_function("aabxaab")
[7, 1, 0, 0, 3, 1, 0]

Constraints
-----------
- len(text), len(pattern) <= 10**5.

Approach ladder
---------------
1. Brute force — compare pattern at every start. O(n m) worst case ("aaaa...a" / "aa...ab").
2. Stdlib     — loop ``text.find(pattern, i + 1)``: what you write in an interview unless
   asked to implement matching. Same results; the C implementation is fast but not
   guaranteed O(n + m) for every input across versions.
3. Optimal    — KMP: on a mismatch after k matched characters, fall back to pi[k-1] instead of
   restarting; the text pointer never moves backwards. O(n + m) time, O(m) space.
   Why move up: the brute force re-reads text characters it has already matched.
   Z-function: same O(n + m) via a [l, r) window of the rightmost match.

Follow-ups
----------
- Repeated-substring pattern: s is periodic iff shortest_period(s) < len(s).
- Shortest palindrome by prepending: prefix_function(s + "#" + s[::-1]).
- Count distinct borders: follow pi[n-1], pi[pi[n-1]-1], ... down to 0.
"""
from __future__ import annotations


def prefix_function(s: str) -> list[int]:
    pi = [0] * len(s)
    k = 0                                # length of the current border
    for i in range(1, len(s)):
        while k and s[i] != s[k]:
            k = pi[k - 1]                # fall back to the next shorter border
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi


def kmp_search(text: str, pattern: str) -> list[int]:
    m = len(pattern)
    if m == 0:
        return list(range(len(text) + 1))
    pi, k, hits = prefix_function(pattern), 0, []
    for i, ch in enumerate(text):
        while k and ch != pattern[k]:
            k = pi[k - 1]
        if ch == pattern[k]:
            k += 1
        if k == m:                       # full match ending at i
            hits.append(i - m + 1)
            k = pi[k - 1]                # keep going: overlaps allowed
    return hits


def brute_search(text: str, pattern: str) -> list[int]:
    m = len(pattern)
    return [i for i in range(len(text) - m + 1) if text[i:i + m] == pattern]


def find_all(text: str, pattern: str) -> list[int]:
    hits, i = [], text.find(pattern)
    while i != -1:
        hits.append(i)
        if i == len(text):               # empty pattern at the end: stop
            break
        i = text.find(pattern, i + 1)
    return hits


def shortest_period(s: str) -> int:
    if not s:
        return 0
    p = len(s) - prefix_function(s)[-1]
    return p if len(s) % p == 0 else len(s)


def z_function(s: str) -> list[int]:
    n = len(s)
    z = [0] * n
    l = r = 0                            # s[l:r] matches a prefix of s, r maximal so far
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])  # reuse the mirror inside the window
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    if n:
        z[0] = n
    return z


def z_search(text: str, pattern: str) -> list[int]:
    m = len(pattern)
    if m == 0:
        return list(range(len(text) + 1))
    z = z_function(pattern + text)       # no separator needed: test z >= m
    return [i - m for i in range(m, m + len(text) - m + 1) if z[i] >= m]


def main() -> None:
    for s in ["aabaaab", "abcabd", "aaaa", "abacaba"]:
        print(f"pi({s!r:<10}) = {prefix_function(s)}   z = {z_function(s)}")
    for text, pat in [("abababa", "aba"), ("aaaaa", "aa"), ("hello", "xyz"), ("abc", ""), ("", "a")]:
        print(f"search({text!r}, {pat!r}): kmp={kmp_search(text, pat)} z={z_search(text, pat)} "
              f"find={find_all(text, pat)} brute={brute_search(text, pat)}")
    for s in ["abcabcabc", "abcab", "aaaa", "a", ""]:
        print(f"shortest_period({s!r}) = {shortest_period(s)}")


if __name__ == "__main__":
    main()
