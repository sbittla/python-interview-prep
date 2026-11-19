"""
Exercise 01 — Trie: insert, search, starts_with, delete with pruning     [Tier: ★ Core]
Chapter 17 · Pattern: trie (prefix tree) · Target time: 25 min

Problem
-------
Implement a set of lowercase words as a trie with four operations:
- insert(word)        add the word (inserting it twice changes nothing);
- search(word)        True if the exact word was inserted;
- starts_with(prefix) True if some stored word begins with prefix;
- delete(word)        remove the word and return True, or return False if it was absent.
  Deleting must PRUNE: every node that no longer lies on the path of a stored word is
  removed, so node_count() always equals 1 + the number of distinct non-empty prefixes
  of the stored words.
Also write ArrayTrie, the same structure with a fixed 26-slot child list per node
(insert / search / starts_with only), to compare the two node layouts.

Examples
--------
>>> t = Trie()
>>> for w in ["apple", "app", "apply"]: t.insert(w)
>>> t.search("app"), t.search("ap"), t.starts_with("ap"), t.node_count()
(True, False, True, 7)
>>> t.delete("apple"), t.node_count(), t.search("apply")
(True, 6, True)

Constraints
-----------
- Words are 1..50 lowercase letters a-z; up to 10^4 operations.

Hints
-----
- A node is a dict of children plus an is_word flag. The root represents "".
- search and starts_with share one walk; they differ only in the final check.
- For delete, remember the path (parent, letter) while walking down, then walk back up
  removing childless nodes that are not the end of another word.

Approach ladder
---------------
1. Brute force — keep a Python set. search is O(L) average (hash), but starts_with scans every
   word: O(n * L). Fine for a handful of words, hopeless for autocomplete.
2. Optimal    — trie. insert / search / starts_with / delete are O(L) regardless of n;
   memory is O(total characters) nodes in the worst case, less when prefixes are shared.
   Why move up: prefix queries become a single walk instead of a scan of the whole set.
3. Layout choice — dict children (only the letters used, any alphabet) vs 26-slot list
   (O(1) index arithmetic, but 26 slots per node even when one is used).

Wrong-but-tempting
------------------
- delete that only clears is_word: answers are right but dead nodes pile up, and
  starts_with(prefix of a deleted word) wrongly returns True.
- starts_with that returns `node is not None` — correct only if the trie is always pruned.
- Pruning that stops at the first node with is_word False instead of checking children.

Follow-ups
----------
- Count words with a given prefix (store a pass count per node, Ex 03).
- Multiset semantics: store a count instead of a bool at word ends.
- Very large dictionaries: compress single-child chains (radix tree) or use a DAWG.
"""
from __future__ import annotations


class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_word = False


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_word = True

    def _walk(self, s: str) -> TrieNode | None:
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        node = self._walk(prefix)
        return node is not None and (node.is_word or bool(node.children))

    def delete(self, word: str) -> bool:
        path: list[tuple[TrieNode, str]] = []       # (parent, letter) for each step
        node = self.root
        for ch in word:
            child = node.children.get(ch)
            if child is None:
                return False
            path.append((node, ch))
            node = child
        if not node.is_word:
            return False
        node.is_word = False
        for parent, ch in reversed(path):           # prune bottom-up
            child = parent.children[ch]
            if child.children or child.is_word:
                break                               # still on another word's path
            del parent.children[ch]
        return True

    def node_count(self) -> int:
        count, stack = 0, [self.root]
        while stack:
            node = stack.pop()
            count += 1
            stack.extend(node.children.values())
        return count

    def words(self) -> list[str]:
        out: list[str] = []
        stack = [(self.root, "")]
        while stack:
            node, prefix = stack.pop()
            if node.is_word:
                out.append(prefix)
            stack.extend((child, prefix + ch) for ch, child in node.children.items())
        return sorted(out)

    def render(self) -> list[str]:
        lines: list[str] = []

        def go(node: TrieNode, depth: int) -> None:
            for ch in sorted(node.children):
                child = node.children[ch]
                lines.append("  " * depth + ch + ("*" if child.is_word else ""))
                go(child, depth + 1)

        go(self.root, 0)
        return lines


class ArrayTrie:
    """Same trie with a fixed 26-slot child list per node (lowercase a-z only)."""

    def __init__(self) -> None:
        self.root: list = [None] * 27               # slots 0..25 children, slot 26 is_word

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            i = ord(ch) - 97
            if node[i] is None:
                node[i] = [None] * 27
            node = node[i]
        node[26] = True

    def _walk(self, s: str) -> list | None:
        node = self.root
        for ch in s:
            node = node[ord(ch) - 97]
            if node is None:
                return None
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node[26] is True

    def starts_with(self, prefix: str) -> bool:
        node = self._walk(prefix)
        return node is not None and any(x is not None for x in node)


class SetBaseline:
    """Rung 1: a plain set; starts_with is a linear scan."""

    def __init__(self) -> None:
        self.words: set[str] = set()

    def insert(self, word: str) -> None:
        self.words.add(word)

    def search(self, word: str) -> bool:
        return word in self.words

    def starts_with(self, prefix: str) -> bool:
        return any(w.startswith(prefix) for w in self.words)

    def delete(self, word: str) -> bool:
        if word in self.words:
            self.words.remove(word)
            return True
        return False


def main() -> None:
    t = Trie()
    for w in ["apple", "app", "apply", "bat"]:
        t.insert(w)
    print("trie (* = end of word):")
    for line in t.render():
        print("  " + line)
    print("nodes:", t.node_count())
    print("search app/ap/apples:", t.search("app"), t.search("ap"), t.search("apples"))
    print("starts_with ap/ba/c:", t.starts_with("ap"), t.starts_with("ba"), t.starts_with("c"))
    print("delete apple:", t.delete("apple"), "-> nodes", t.node_count(), "(pruned 'e')")
    print("delete app  :", t.delete("app"), "-> nodes", t.node_count(), "(path kept for apply)")
    print("delete ap   :", t.delete("ap"), "(not a word)")
    print("delete bat  :", t.delete("bat"), "-> nodes", t.node_count(), "(whole branch pruned)")
    print("words left  :", t.words())
    a = ArrayTrie()
    for w in ["apple", "app"]:
        a.insert(w)
    print("array trie  :", a.search("app"), a.search("ap"), a.starts_with("appl"))


if __name__ == "__main__":
    main()
