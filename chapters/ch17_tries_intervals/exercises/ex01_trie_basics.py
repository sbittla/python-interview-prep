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
        raise NotImplementedError("TODO")

    def _walk(self, s: str) -> TrieNode | None:
        raise NotImplementedError("TODO")

    def search(self, word: str) -> bool:
        raise NotImplementedError("TODO")

    def starts_with(self, prefix: str) -> bool:
        raise NotImplementedError("TODO")

    def delete(self, word: str) -> bool:
        raise NotImplementedError("TODO")

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
        raise NotImplementedError("TODO")

    def _walk(self, s: str) -> list | None:
        raise NotImplementedError("TODO")

    def search(self, word: str) -> bool:
        raise NotImplementedError("TODO")

    def starts_with(self, prefix: str) -> bool:
        raise NotImplementedError("TODO")


class SetBaseline:
    """Rung 1: a plain set; starts_with is a linear scan."""

    def __init__(self) -> None:
        self.words: set[str] = set()

    def insert(self, word: str) -> None:
        raise NotImplementedError("TODO")

    def search(self, word: str) -> bool:
        raise NotImplementedError("TODO")

    def starts_with(self, prefix: str) -> bool:
        raise NotImplementedError("TODO")

    def delete(self, word: str) -> bool:
        raise NotImplementedError("TODO")


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
