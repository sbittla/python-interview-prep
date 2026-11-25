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

Approach ladder
---------------
Word break recipe — state: ok(i) = s[:i] can be split; transition: ok(i) = any(ok(j)
and s[j:i] in words) for i - maxlen <= j < i; base: ok(0) = True; order: i ascending;
answer: ok(n).
1. Plain recursion — try every word at every position: O(2^n) on inputs like
   "aaaa...ab" with words {"a", "aa", "aaa"}.
2. Memoised on position — n states, each tries all W words with startswith (O(L)
   each, L = longest word): O(n * W * L) time, O(n) space; recursion depth ~n (fails
   at n = 1000): hits the ~1000 limit (section 7.21) well inside the constraints; this is why we move to the table.
3. Bottom-up table — for each i try only the L cut points j in [i - L, i); slicing and
   hashing s[j:i] costs O(L): O(n * L^2) time, O(n) space; parent[i] = j rebuilds a
   split. (A rolling window of L + 1 cells would answer True/False, but not the split.)
Palindromic substrings — state: pal(i, j) = s[i..j] is a palindrome; transition:
s[i] == s[j] and (j - i < 2 or pal(i+1, j-1)); order: i descending (pal(i+1, ..) first).
Brute O(n^3) -> table O(n^2) time and space -> expand around 2n-1 centres O(n^2) time,
O(1) space (section 9.5, Chapter 9 exercise 09).
Longest palindromic subsequence — state: P(i, j) for s[i..j]; transition: 2 + P(i+1, j-1)
if s[i] == s[j] else max(P(i+1, j), P(i, j-1)); base P(i, i) = 1, P(i, i-1) = 0;
order: i descending, j ascending; answer P(0, n-1).
Recursion O(2^n) -> memo O(n^2) -> table O(n^2) space -> two rows O(n) space.
Also LPS(s) = LCS(s, s[::-1]).

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
    def ok(i: int) -> bool:                     # can s[i:] be split?
        if i == len(s):
            return True
        return any(s.startswith(w, i) and ok(i + len(w)) for w in words)

    return ok(0)


def word_break_memo(s: str, words: set[str]) -> bool:
    @cache
    def ok(i: int) -> bool:
        if i == len(s):
            return True
        return any(s.startswith(w, i) and ok(i + len(w)) for w in words)

    return ok(0)


def _parents(s: str, words: set[str]) -> list[int | None]:
    longest = max(map(len, words), default=0)
    parent: list[int | None] = [None] * (len(s) + 1)
    parent[0] = 0                               # ok(0) is True
    for i in range(1, len(s) + 1):
        for j in range(max(0, i - longest), i):
            if parent[j] is not None and s[j:i] in words:
                parent[i] = j
                break
    return parent


def word_break(s: str, words: set[str]) -> bool:
    return _parents(s, words)[-1] is not None


def word_break_split(s: str, words: set[str]) -> list[str] | None:
    parent = _parents(s, words)
    if parent[-1] is None:
        return None
    out, i = [], len(s)
    while i:
        j = parent[i]
        out.append(s[j:i])
        i = j
    return out[::-1]


# ---------------------------------------------------------------- palindromic substrings
def count_pal_substrings_brute(s: str) -> int:
    return sum(s[i:j] == s[i:j][::-1] for i in range(len(s)) for j in range(i + 1, len(s) + 1))


def count_pal_substrings_table(s: str) -> int:
    n, total = len(s), 0
    pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
                total += 1
    return total


def count_pal_substrings(s: str) -> int:
    total = 0
    for centre in range(2 * len(s) - 1):        # characters and gaps
        lo, hi = centre // 2, (centre + 1) // 2
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            total += 1
            lo, hi = lo - 1, hi + 1
    return total


# ---------------------------------------------------------------- longest palindromic subsequence
def lps_brute(s: str) -> int:
    def best(i: int, j: int) -> int:
        if i > j:
            return 0
        if i == j:
            return 1
        if s[i] == s[j]:
            return 2 + best(i + 1, j - 1)
        return max(best(i + 1, j), best(i, j - 1))

    return best(0, len(s) - 1)


def lps_memo(s: str) -> int:
    @cache
    def best(i: int, j: int) -> int:
        if i > j:
            return 0
        if i == j:
            return 1
        if s[i] == s[j]:
            return 2 + best(i + 1, j - 1)
        return max(best(i + 1, j), best(i, j - 1))

    return best(0, len(s) - 1)


def lps_table(s: str) -> int:
    n = len(s)
    if n == 0:
        return 0
    P = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        P[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                P[i][j] = 2 + (P[i + 1][j - 1] if i + 1 <= j - 1 else 0)
            else:
                P[i][j] = max(P[i + 1][j], P[i][j - 1])
    return P[0][n - 1]


def lps(s: str) -> int:
    n = len(s)
    below = [0] * n                             # row i + 1 of the table
    for i in range(n - 1, -1, -1):
        row = [0] * n
        row[i] = 1
        for j in range(i + 1, n):
            row[j] = below[j - 1] + 2 if s[i] == s[j] else max(below[j], row[j - 1])
        below = row
    return below[n - 1] if n else 0


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
