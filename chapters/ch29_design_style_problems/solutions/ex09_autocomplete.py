"""
Exercise 09 — Autocomplete System (trie-based)     [Tier: ★ Core]
Chapter 29 · Pattern: trie + per-node top-k cache · Target time: 40 min

Problem
-------
A search box suggests completions while the user types.

    ac = Autocomplete(sentences, counts, k=3)
    ac.suggest(prefix)   -> up to k stored sentences starting with prefix, ranked by
                            higher count first, then alphabetical (ASCII) order
    ac.record(sentence)  -> None; the user submitted a query: count += 1 (new if unseen)
    ac.type(ch)          -> streaming API: append ch to the current input and return
                            suggest(current input); ch == "#" submits the current input
                            (records it), resets the input and returns []

Examples
--------
>>> ac = Autocomplete(["i love you", "island", "ironman", "i love coding"], [5, 3, 2, 2])
>>> ac.suggest("i ")
['i love you', 'i love coding']
>>> ac.suggest("i")
['i love you', 'island', 'i love coding']

Constraints
-----------
- Up to 10**4 stored sentences of length <= 100; up to 10**4 calls; k <= 10.

Approach ladder
---------------
1. Brute force — scan every sentence, keep those with the prefix, sort: O(N * L + M log M)
   per keystroke.
2. Improved   — a trie; walk to the prefix node (O(P)), then DFS the subtree collecting
   sentences and take the top k with a heap: O(P + subtree size).
3. Optimal for read-heavy workloads — cache the top-k list *in every trie node*. A query
   is O(P + k). `record` walks the sentence's path and refreshes each node's cache:
   O(L * k log k). Reads (every keystroke) vastly outnumber writes (submissions), so we
   move the work to the write path.

Hints
-----
- Rank key: `(-count, sentence)` — sorting by it gives the required order.
- In the streaming API, remember the current trie node so each keystroke is O(1) + k;
  once the prefix falls off the trie, return [] until '#'.

Follow-ups
----------
- Personalisation (blend global and per-user counts), recency decay, typo tolerance
  (edit distance <= 1), sharding the trie by first letter for scale.
"""
from __future__ import annotations

import heapq


class AutocompleteBrute:
    def __init__(self, sentences: list[str], counts: list[int], k: int = 3) -> None:
        self.counts = dict(zip(sentences, counts))
        self.k = k

    def record(self, sentence: str) -> None:
        self.counts[sentence] = self.counts.get(sentence, 0) + 1

    def suggest(self, prefix: str) -> list[str]:
        hits = [s for s in self.counts if s.startswith(prefix)]
        return sorted(hits, key=lambda s: (-self.counts[s], s))[: self.k]


class TrieNode:
    __slots__ = ("children", "top")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.top: list[str] = []        # cached best-k sentences in this subtree


class Autocomplete:
    def __init__(self, sentences: list[str], counts: list[int], k: int = 3) -> None:
        self.k = k
        self.root = TrieNode()
        self.counts: dict[str, int] = {}
        for s, c in zip(sentences, counts):
            self.counts[s] = self.counts.get(s, 0) + c
        for s in self.counts:
            self._refresh_path(s)
        self.buffer = ""
        self.cursor: TrieNode | None = self.root

    def _rank(self, s: str) -> tuple[int, str]:
        return (-self.counts[s], s)

    def _refresh_path(self, sentence: str) -> None:
        """Insert sentence's path and update the top-k cache of every node on it."""
        for node in self._path(sentence):
            if sentence not in node.top:
                node.top.append(sentence)
            node.top.sort(key=self._rank)
            del node.top[self.k:]

    def _path(self, sentence: str):
        node = self.root
        yield node
        for ch in sentence:
            node = node.children.setdefault(ch, TrieNode())
            yield node

    def record(self, sentence: str) -> None:
        self.counts[sentence] = self.counts.get(sentence, 0) + 1
        self._refresh_path(sentence)     # counts only grow, so caches stay correct

    def suggest(self, prefix: str) -> list[str]:
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return []
        return list(node.top)

    def suggest_dfs(self, prefix: str) -> list[str]:
        """Rung 2 (no caches): walk the subtree and pick the best k with a heap."""
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return []
        found: list[str] = []
        stack = [(node, prefix)]
        while stack:
            cur, text = stack.pop()
            if text in self.counts:
                found.append(text)
            for ch, child in cur.children.items():
                stack.append((child, text + ch))
        return heapq.nsmallest(self.k, found, key=self._rank)

    def type(self, ch: str) -> list[str]:
        if ch == "#":
            if self.buffer:
                self.record(self.buffer)
            self.buffer, self.cursor = "", self.root
            return []
        self.buffer += ch
        if self.cursor is not None:
            self.cursor = self.cursor.children.get(ch)
        return list(self.cursor.top) if self.cursor else []


def main() -> None:
    sentences = ["i love you", "island", "ironman", "i love coding", "iris", "ice cream"]
    counts = [5, 3, 2, 2, 2, 1]
    ac = Autocomplete(sentences, counts)
    brute = AutocompleteBrute(sentences, counts)
    for p in ["i", "i ", "ir", "is", "x", ""]:
        print(f"suggest({p!r:<5}) -> {ac.suggest(p)}   dfs agrees: {ac.suggest_dfs(p) == brute.suggest(p) == ac.suggest(p)}")

    print("\nstreaming input 'i a#' then 'i a' again:")
    for ch in "i a#i a":
        print(f"  type({ch!r}) -> {ac.type(ch)}")
    for _ in range(3):
        ac.record("iris")
    print("after 3 more 'iris' searches, suggest('i') ->", ac.suggest("i"))


if __name__ == "__main__":
    main()
