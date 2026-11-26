"""
Exercise 07 — Group Anagrams                              [Tier: ★ Core]
Chapter 09 · Pattern: grouping by canonical key · Target time: 15 min

Problem
-------
Given a list of lowercase words, group together the words that are anagrams of
each other. Return the groups with words inside each group sorted, and the
groups sorted by their first word (so the output is deterministic).

Examples
--------
>>> solve(["eat", "tea", "tan", "ate", "nat", "bat"])
[['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']]

Constraints
-----------
- 0 <= len(words) <= 10**4; 0 <= len(word) <= 100; letters a-z only.

Approach ladder
---------------
1. Brute force — compare every word against a representative of every existing
   group with a sorted() anagram check. O(n * g * L log L) for g groups, i.e.
   O(n^2 * L log L) when every word is its own group.
2. Improved   — key = "".join(sorted(word)); dict key -> list. O(n * L log L).
3. Optimal    — key = tuple of 26 letter counts: O(n * (L + 26)) time. In practice
   sorted() wins for short words because it runs in C; say so in the interview.
   Why move up: a canonical key turns "compare with every group" into one O(1)
   average dict lookup.

Follow-ups
----------
- Unicode words: use the sorted-string key, or a Counter frozen as
  tuple(sorted(Counter(w).items())).
- Group strings that are rotations/shifts of each other ("abc" ~ "bcd"): key is
  the tuple of differences between consecutive letters mod 26.
- Return only groups of size >= 2.
"""
from __future__ import annotations

from collections import defaultdict


def _finish(groups) -> list[list[str]]:
    return sorted(sorted(g) for g in groups)


def brute_force(words: list[str]) -> list[list[str]]:
    groups: list[list[str]] = []
    for w in words:
        for g in groups:
            if sorted(g[0]) == sorted(w):
                g.append(w)
                break
        else:
            groups.append([w])
    return _finish(groups)


def by_sorted_key(words: list[str]) -> list[list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)
    return _finish(groups.values())


def count_key(word: str) -> tuple[int, ...]:
    counts = [0] * 26
    for ch in word:
        counts[ord(ch) - ord("a")] += 1
    return tuple(counts)               # lists are unhashable; tuples are keys


def solve(words: list[str]) -> list[list[str]]:
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)
    for w in words:
        groups[count_key(w)].append(w)
    return _finish(groups.values())


def main() -> None:
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    print("groups:", solve(words))
    print("agree :", solve(words) == by_sorted_key(words) == brute_force(words))
    print("edge  :", solve([]), solve([""]), solve(["", "", "a"]))
    print("key   :", "".join(sorted("listen")), count_key("ab")[:3])


if __name__ == "__main__":
    main()
