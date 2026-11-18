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

Hints
-----
- Anagrams share a canonical key; group words in a dict key -> list.
- Key option 1: ''.join(sorted(word)). Option 2: tuple of 26 letter counts.
- Lists cannot be dict keys; convert to tuple.

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
    raise NotImplementedError("TODO")


def by_sorted_key(words: list[str]) -> list[list[str]]:
    raise NotImplementedError("TODO")


def count_key(word: str) -> tuple[int, ...]:
    raise NotImplementedError("TODO")


def solve(words: list[str]) -> list[list[str]]:
    raise NotImplementedError("TODO")


def main() -> None:
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    print("groups:", solve(words))
    print("agree :", solve(words) == by_sorted_key(words) == brute_force(words))
    print("edge  :", solve([]), solve([""]), solve(["", "", "a"]))
    print("key   :", "".join(sorted("listen")), count_key("ab")[:3])


if __name__ == "__main__":
    main()
