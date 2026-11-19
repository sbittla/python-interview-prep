"""
Exercise 09 — Rabin–Karp Search and Longest Duplicate Substring   [Tier: ★ Core (LDS: ◆)]
Chapter 21 · Pattern: rolling polynomial hash + verification · Target time: 30 min

Problem
-------
1. ``rk_search(text, pattern, mod=..., base=...)``: all start indices of pattern in text
   (overlaps included; empty pattern -> every index 0..len(text)). A hash match must be
   verified by comparing characters, so the answer is correct for *any* modulus.
   ``rk_search_stats`` also reports how many hash hits were spurious (collisions).
2. ◆ ``longest_dup_substring(s)``: a longest substring that occurs at least twice
   (occurrences may overlap); "" if none.

Examples
--------
>>> rk_search("abracadabra", "abra")
[0, 7]
>>> longest_dup_substring("banana")
'ana'

Constraints
-----------
- len(s) <= 3 * 10**4 for the duplicate-substring problem.

Approach ladder
---------------
Search:
1. Brute force — compare at every start. O(n m).
2. Optimal    — hash the window: h(s[i+1:i+m+1]) = (h(s[i:i+m]) - s[i]*B^(m-1)) * B + s[i+m].
   O(n + m) expected; O(n m) worst case if (almost) every window collides, because each hit
   is verified. Why move up: the window update is O(1) instead of O(m).
Longest duplicate substring:
1. Brute force — for L from n-1 down, put every length-L substring in a set. O(n^3) time
   (O(n) slices of length L for each L), O(n^2) space per L.
2. Binary search on L (a duplicate of length L implies one of length L-1), checking each L
   with a set of slices. O(n^2 log n) worst case.
3. Optimal    — the same binary search, checking each L with rolling hashes (hash -> start
   indices, verify on a hit). O(n log n) expected, O(n) space.
   Why move up: slicing costs O(L) per window; rolling costs O(1).

Follow-ups
----------
- Why mod = 2**61 - 1? A large prime makes a collision between two fixed different windows
  unlikely (probability at most (L - 1) / mod over a random base); Python ints make the big
  products overflow-free.
  Never trust a hash match without comparing (or double hashing + accepting risk).
- Dedup use: group documents/lines by hash, then compare only within a group.
"""
from __future__ import annotations

import random

MOD = (1 << 61) - 1                      # a Mersenne prime
BASE = random.Random(21).randrange(256, MOD - 1)   # fixed "random" base: deterministic runs


def rk_search_stats(text: str, pattern: str, mod: int = MOD, base: int = BASE) -> tuple[list[int], int]:
    n, m = len(text), len(pattern)
    if m == 0:
        return list(range(n + 1)), 0
    if m > n:
        return [], 0
    high = pow(base, m - 1, mod)         # weight of the character leaving the window
    hp = hw = 0
    for i in range(m):
        hp = (hp * base + ord(pattern[i])) % mod
        hw = (hw * base + ord(text[i])) % mod
    hits, spurious = [], 0
    for i in range(n - m + 1):
        if hw == hp:
            if text[i:i + m] == pattern:      # verification: never skip it
                hits.append(i)
            else:
                spurious += 1
        if i + m < n:
            hw = ((hw - ord(text[i]) * high) * base + ord(text[i + m])) % mod
    return hits, spurious


def rk_search(text: str, pattern: str, mod: int = MOD, base: int = BASE) -> list[int]:
    return rk_search_stats(text, pattern, mod, base)[0]


def _dup_of_length_hash(s: str, L: int) -> str | None:
    if L == 0:
        return ""
    high = pow(BASE, L - 1, MOD)
    h = 0
    for i in range(L):
        h = (h * BASE + ord(s[i])) % MOD
    seen: dict[int, list[int]] = {h: [0]}
    for i in range(1, len(s) - L + 1):
        h = ((h - ord(s[i - 1]) * high) * BASE + ord(s[i - 1 + L])) % MOD
        window = s[i:i + L]
        starts = seen.setdefault(h, [])
        if any(s[j:j + L] == window for j in starts):     # verify against true matches
            return window
        starts.append(i)
    return None


def _dup_of_length_set(s: str, L: int) -> str | None:
    seen: set[str] = set()
    for i in range(len(s) - L + 1):
        w = s[i:i + L]
        if w in seen:
            return w
        seen.add(w)
    return None


def _binary_search(s: str, check) -> str:
    lo, hi, best = 1, len(s) - 1, ""
    while lo <= hi:
        mid = (lo + hi) // 2
        found = check(s, mid)
        if found is not None:
            best, lo = found, mid + 1
        else:
            hi = mid - 1
    return best


def longest_dup_brute(s: str) -> str:
    for L in range(len(s) - 1, 0, -1):
        found = _dup_of_length_set(s, L)
        if found is not None:
            return found
    return ""


def longest_dup_slices(s: str) -> str:
    return _binary_search(s, _dup_of_length_set)


def longest_dup_substring(s: str) -> str:
    return _binary_search(s, _dup_of_length_hash)


def main() -> None:
    for text, pat in [("abracadabra", "abra"), ("aaaaa", "aaa"), ("abc", "d"), ("abc", "")]:
        print(f"rk_search({text!r}, {pat!r}) = {rk_search(text, pat)}")
    rng = random.Random(7)
    text = "".join(rng.choice("abcd") for _ in range(2000))
    hits, spurious = rk_search_stats(text, "abca", mod=101, base=31)
    good, _ = rk_search_stats(text, "abca")
    brute = [i for i in range(len(text) - 3) if text[i:i + 4] == "abca"]
    print(f"tiny mod 101: matches={len(hits)} spurious hash hits={spurious} correct={hits == brute}")
    print(f"mod 2**61-1 : matches={len(good)} correct={good == brute}")
    for s in ["banana", "abcd", "aaaaa", "abcabcab", "", "mississippi"]:
        print(f"longest_dup({s!r}) = {longest_dup_substring(s)!r}  brute={longest_dup_brute(s)!r}  "
              f"slices={longest_dup_slices(s)!r}")


if __name__ == "__main__":
    main()
