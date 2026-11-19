"""
Exercise 03 — Prefix counting and top-3 suggestions             [Tier: ★ Core]
Chapter 17 · Pattern: trie with per-node aggregates · Target time: 25 min

Problem
-------
Part A. PrefixCounter stores distinct lowercase words:
- insert(word) -> bool          False if the word was already present;
- count_prefix(prefix) -> int   how many stored words start with prefix ("" counts all).

Part B. suggestions(products, typed): products is a list of distinct lowercase words. After
each character of `typed` is entered, report up to three products that start with the text
typed so far, smallest first in lexicographic order. Return one list per character.
(This is the trie mechanics only; the full autocomplete service is Chapter 29.)

Examples
--------
>>> pc = PrefixCounter()
>>> for w in ["car", "card", "care", "cat", "dog"]: _ = pc.insert(w)
>>> pc.count_prefix("car"), pc.count_prefix("ca"), pc.count_prefix("x"), pc.count_prefix("")
(3, 4, 0, 5)
>>> suggestions(["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mou")
[['mobile', 'moneypot', 'monitor'], ['mobile', 'moneypot', 'monitor'], ['mouse', 'mousepad']]

Constraints
-----------
- Up to 10^4 products, total length <= 2 * 10^4; len(typed) <= 1000.

Hints
-----
- Part A: store at each node how many words pass through it; the answer is that counter at
  the end of the prefix walk.
- Part B (sorted list): the matches for a prefix form one contiguous block of the sorted
  list; bisect_left finds where it starts.
- Part B (trie): insert products in sorted order and let each node keep the first three
  words that pass through it.

Follow-ups
----------
- Rank by frequency instead of alphabetically: store (−count, word) and keep a bounded heap.
- Deletions: per-node top-k lists become stale; recompute along the path or use counters.
"""
from __future__ import annotations

from bisect import bisect_left


class _Node:
    __slots__ = ("children", "is_word", "passes", "top")

    def __init__(self) -> None:
        self.children: dict[str, _Node] = {}
        self.is_word = False
        self.passes = 0                  # number of stored words in this subtree
        self.top: list[str] = []         # up to 3 smallest words in this subtree


class PrefixCounter:
    def __init__(self) -> None:
        self.root = _Node()

    def insert(self, word: str) -> bool:
        raise NotImplementedError("TODO")

    def count_prefix(self, prefix: str) -> int:
        raise NotImplementedError("TODO")


def count_prefix_brute(words: list[str], prefix: str) -> int:
    raise NotImplementedError("TODO")


def suggestions_brute(products: list[str], typed: str) -> list[list[str]]:
    raise NotImplementedError("TODO")


def suggestions_bisect(products: list[str], typed: str) -> list[list[str]]:
    raise NotImplementedError("TODO")


def suggestions(products: list[str], typed: str) -> list[list[str]]:
    raise NotImplementedError("TODO")


def main() -> None:
    pc = PrefixCounter()
    for w in ["car", "card", "care", "cat", "dog", "car"]:
        pc.insert(w)
    for p in ["car", "ca", "c", "", "dogs", "x"]:
        print(f"count_prefix({p!r:6}) -> {pc.count_prefix(p)}")
    products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"]
    for typed in ["mouse", "mx", "z"]:
        print(f"suggestions({typed!r}):")
        for i, row in enumerate(suggestions(products, typed), 1):
            print(f"  {typed[:i]:6} -> {row}")
    print("all rungs agree:", suggestions(products, "mouse") == suggestions_bisect(products, "mouse")
          == suggestions_brute(products, "mouse"))


if __name__ == "__main__":
    main()
