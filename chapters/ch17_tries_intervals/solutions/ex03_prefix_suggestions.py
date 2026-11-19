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

Approach ladder
---------------
1. Brute force — for each typed prefix, filter and sort all products. O(m * n log n) for
   m typed characters (Part A: scan all words, O(n * L)).
2. Improved   — sort once, then bisect per prefix and read up to three neighbours.
   O(n log n * L + m * (L log n)) — often the best interview answer: short and fast.
3. Trie       — node counters give count_prefix in O(len(prefix)); per-node top-3 lists
   give each suggestion list in O(1) after the walk. Build O(total chars); memory is
   higher. Why move up: the per-keystroke cost no longer depends on n, and the walk is
   incremental (one step per typed character, never restarting from the root).

Wrong-but-tempting
------------------
- Restarting the walk from the root for every prefix: correct, but O(m^2) on long input.
- Continuing to look up later prefixes after a miss: once a prefix has no node, every
  longer prefix is empty too.
- Keeping "top 3" at a node without inserting in sorted order (needs a sort per node).

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
        node = self.root
        for ch in word:
            node = node.children.get(ch)
            if node is None:
                break
        else:
            if node.is_word:
                return False             # already present: counters unchanged
        node = self.root
        node.passes += 1
        for ch in word:
            node = node.children.setdefault(ch, _Node())
            node.passes += 1
        node.is_word = True
        return True

    def count_prefix(self, prefix: str) -> int:
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return 0
        return node.passes


def count_prefix_brute(words: list[str], prefix: str) -> int:
    return sum(w.startswith(prefix) for w in set(words))


def suggestions_brute(products: list[str], typed: str) -> list[list[str]]:
    return [sorted(p for p in products if p.startswith(typed[:i]))[:3]
            for i in range(1, len(typed) + 1)]


def suggestions_bisect(products: list[str], typed: str) -> list[list[str]]:
    products = sorted(products)
    out = []
    for i in range(1, len(typed) + 1):
        prefix = typed[:i]
        j = bisect_left(products, prefix)
        out.append([p for p in products[j:j + 3] if p.startswith(prefix)])
    return out


def suggestions(products: list[str], typed: str) -> list[list[str]]:
    root = _Node()
    for word in sorted(products):        # sorted insert => first 3 seen are the smallest
        node = root
        for ch in word:
            node = node.children.setdefault(ch, _Node())
            if len(node.top) < 3:
                node.top.append(word)
    out: list[list[str]] = []
    node: _Node | None = root
    for ch in typed:                     # one step per keystroke, never restart
        node = node.children.get(ch) if node else None
        out.append(list(node.top) if node else [])
    return out


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
