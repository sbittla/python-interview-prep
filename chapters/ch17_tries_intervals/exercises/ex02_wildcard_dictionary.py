"""
Exercise 02 — Word dictionary with '.' wildcards                [Tier: ★ Core]
Chapter 17 · Pattern: trie + DFS over branches · Target time: 20 min

Problem
-------
Design a dictionary of lowercase words with two operations:
- add_word(word)   store the word;
- search(pattern)  True if some stored word has the same length as pattern and matches it,
                   where '.' in the pattern matches any single letter.

Examples
--------
>>> d = WordDictionary()
>>> for w in ["bad", "dad", "mad"]: d.add_word(w)
>>> d.search("pad"), d.search("bad"), d.search(".ad"), d.search("b.."), d.search("b.")
(False, True, True, True, False)

Constraints
-----------
- Words and patterns: 1..25 characters; at most 3 dots per pattern; up to 10^4 calls.

Hints
-----
- Letters follow one child; a dot must try every child (branch).
- Use an explicit stack of (node, index) pairs, or recursion: depth is at most 25.

Follow-ups
----------
- Support '*' (any run of letters): the DFS gains a "consume one letter, stay on '*'" branch.
- Return all matches instead of True/False.
"""
from __future__ import annotations


class _Node:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, _Node] = {}
        self.is_word = False


class WordDictionary:
    def __init__(self) -> None:
        self.root = _Node()

    def add_word(self, word: str) -> None:
        raise NotImplementedError("TODO")

    def search(self, pattern: str) -> bool:
        raise NotImplementedError("TODO")


def _matches(word: str, pattern: str) -> bool:
    return len(word) == len(pattern) and all(p in (".", c) for c, p in zip(word, pattern))


class BruteDictionary:
    def __init__(self) -> None:
        self.words: list[str] = []

    def add_word(self, word: str) -> None:
        raise NotImplementedError("TODO")

    def search(self, pattern: str) -> bool:
        raise NotImplementedError("TODO")


class LengthBucketDictionary:
    def __init__(self) -> None:
        self.by_len: dict[int, list[str]] = {}

    def add_word(self, word: str) -> None:
        raise NotImplementedError("TODO")

    def search(self, pattern: str) -> bool:
        raise NotImplementedError("TODO")


def main() -> None:
    d = WordDictionary()
    for w in ["bad", "dad", "mad", "bat"]:
        d.add_word(w)
    for p in ["pad", "bad", ".ad", "b..", "b.", "...", "....", "..t", ".a."]:
        print(f"search({p!r:7}) -> {d.search(p)}")
    brute = BruteDictionary()
    for w in ["bad", "dad", "mad", "bat"]:
        brute.add_word(w)
    print("agrees with brute force:", all(d.search(p) == brute.search(p)
                                          for p in ["pad", ".ad", "b.", "..t", "z.."]))


if __name__ == "__main__":
    main()
