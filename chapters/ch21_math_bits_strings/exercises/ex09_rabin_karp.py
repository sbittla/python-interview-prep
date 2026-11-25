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

Hints
-----
- Polynomial hash h = s[0]*B^(m-1) + ... + s[m-1] mod M; slide with
  (h - out*B^(m-1)) * B + in.
- On a hash match, compare the slices before reporting it.
- Longest duplicate: binary search on the length L; check one L with a dict hash -> starts.

Wrong-but-tempting
------------------
- Trusting a hash match without comparing characters.
- A tiny modulus such as 101 or a fixed base an adversary can target.
- Binary search with ``hi = len(s)``: a substring of length n cannot occur twice.

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
    raise NotImplementedError("TODO")


def rk_search(text: str, pattern: str, mod: int = MOD, base: int = BASE) -> list[int]:
    raise NotImplementedError("TODO")


def _dup_of_length_hash(s: str, L: int) -> str | None:
    raise NotImplementedError("TODO")


def _dup_of_length_set(s: str, L: int) -> str | None:
    raise NotImplementedError("TODO")


def _binary_search(s: str, check) -> str:
    raise NotImplementedError("TODO")


def longest_dup_brute(s: str) -> str:
    raise NotImplementedError("TODO")


def longest_dup_slices(s: str) -> str:
    raise NotImplementedError("TODO")


def longest_dup_substring(s: str) -> str:
    raise NotImplementedError("TODO")


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
