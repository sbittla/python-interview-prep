"""
Exercise 04 — Word Search II: many words, one grid               [Tier: ◆ Extended]
Chapter 17 · Pattern: trie + grid backtracking with pruning · Target time: 35 min

Problem
-------
Given a grid of lowercase letters and a list of words, return (sorted, without duplicates)
every word that can be traced through horizontally or vertically adjacent cells, using each
cell at most once per word. Builds on single-word search (Chapter 18, Ex 10).

Examples
--------
>>> board = [list("oaan"), list("etae"), list("ihkr"), list("iflv")]
>>> solve(board, ["oath", "pea", "eat", "rain"])
['eat', 'oath']

Constraints
-----------
- 1 <= rows, cols <= 12; up to 3 * 10^4 words of length 1..10.

Hints
-----
- Put all words in a trie and store the complete word at its end node.
- Run one DFS per start cell; follow the trie child for the cell's letter, and stop as soon
  as there is no such child — no word continues that way.
- When you find a word, clear it from its node so it is reported once; then delete trie
  nodes that have become empty so later searches never enter them.

Follow-ups
----------
- Diagonal moves: 8 directions, same code.
- Count occurrences of every word instead of existence.
"""
from __future__ import annotations

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def exists(board: list[list[str]], word: str) -> bool:
    """Single-word search (Chapter 18, Ex 10), used by the brute-force rung."""
    rows, cols = len(board), len(board[0])

    def dfs(r: int, c: int, k: int) -> bool:
        if board[r][c] != word[k]:
            return False
        if k == len(word) - 1:
            return True
        saved, board[r][c] = board[r][c], "#"
        found = any(0 <= r + dr < rows and 0 <= c + dc < cols and dfs(r + dr, c + dc, k + 1)
                    for dr, dc in DIRS)
        board[r][c] = saved
        return found

    return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))


def brute_force(board: list[list[str]], words: list[str]) -> list[str]:
    raise NotImplementedError("TODO")


class _Node:
    __slots__ = ("children", "word")

    def __init__(self) -> None:
        self.children: dict[str, _Node] = {}
        self.word: str | None = None


def _build(words: list[str]) -> _Node:
    root = _Node()
    for w in words:
        node = root
        for ch in w:
            node = node.children.setdefault(ch, _Node())
        node.word = w
    return root


def solve(board: list[list[str]], words: list[str], prune: bool = True,
          stats: dict | None = None) -> list[str]:
    raise NotImplementedError("TODO")


def main() -> None:
    board = [list("oaan"), list("etae"), list("ihkr"), list("iflv")]
    words = ["oath", "pea", "eat", "rain", "oat", "oath"]
    print("found:", solve(board, words))
    print("brute:", brute_force(board, words))
    print("board restored:", ["".join(r) for r in board] == ["oaan", "etae", "ihkr", "iflv"])
    # Pruning pays off when words are found early: a grid of 'a' and words a, aa, ..., a^6.
    grid = [["a"] * 4 for _ in range(4)]
    many = ["a" * k for k in range(1, 7)]
    s1: dict = {}
    s2: dict = {}
    r1 = solve([row[:] for row in grid], many, prune=False, stats=s1)
    r2 = solve([row[:] for row in grid], many, prune=True, stats=s2)
    print("all-'a' grid, same answer:", r1 == r2, "| pruning makes fewer calls:",
          s2["calls"] < s1["calls"])
    print("edge: 1x1 grid:", solve([["a"]], ["a", "aa", "b"]))


if __name__ == "__main__":
    main()
