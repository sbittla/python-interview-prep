"""
Exercise 10 — Word search in a grid                [Tier: ★ Core]
Chapter 18 · Pattern: grid DFS backtracking (mark / unmark) · Target time: 20 min

Problem
-------
Given a grid of letters and a word, decide whether the word can be traced through horizontally or
vertically adjacent cells, using each cell at most once.

Examples
--------
>>> board = [list("ABCE"), list("SFCS"), list("ADEE")]
>>> solve(board, "ABCCED"), solve(board, "SEE"), solve(board, "ABCB")
(True, True, False)

Constraints
-----------
- 1 <= rows, cols <= 6; 1 <= len(word) <= 15; letters only.

Hints
-----
- Start a DFS from every cell that matches word[0].
- Mark the current cell as used (e.g. overwrite it with '#') before exploring neighbours and
  restore it afterwards — that is the choose / unchoose step.
- Cheap pre-checks: the board must contain enough of every letter of the word.

Approach ladder
---------------
1. Brute force — DFS from every cell carrying a `visited` set copied at each step.
   O(R * C * 4^L) time and extra O(L) copies per step.
2. Optimal    — the same DFS with in-place marking (no copies) plus pruning:
   * letter-count check before searching at all;
   * if the last letter is rarer than the first, search for the reversed word (fewer start cells).
   Worst case still O(R * C * 3^L) (after the first step there are at most 3 unvisited neighbours).

Follow-ups
----------
- Find all dictionary words in the grid at once: build a trie (Chapter 17, word search II).
- Return the path, not just True/False.
"""
from __future__ import annotations

from collections import Counter

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def brute_force(board: list[list[str]], word: str, stats: dict | None = None) -> bool:
    rows, cols = len(board), len(board[0])

    def dfs(r: int, c: int, k: int, visited: frozenset) -> bool:
        if stats is not None:
            stats["calls"] = stats.get("calls", 0) + 1
        if board[r][c] != word[k]:
            return False
        if k == len(word) - 1:
            return True
        visited = visited | {(r, c)}         # copy: simple but wasteful
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                if dfs(nr, nc, k + 1, visited):
                    return True
        return False

    return any(dfs(r, c, 0, frozenset()) for r in range(rows) for c in range(cols))


def solve(board: list[list[str]], word: str, stats: dict | None = None) -> bool:
    rows, cols = len(board), len(board[0])
    have = Counter(ch for row in board for ch in row)
    need = Counter(word)
    if any(have[ch] < cnt for ch, cnt in need.items()):
        return False                         # prune 1: not enough letters at all
    if have[word[0]] > have[word[-1]]:
        word = word[::-1]                    # prune 2: start from the rarer end

    def dfs(r: int, c: int, k: int) -> bool:
        if stats is not None:
            stats["calls"] = stats.get("calls", 0) + 1
        if board[r][c] != word[k]:
            return False
        if k == len(word) - 1:
            return True
        saved, board[r][c] = board[r][c], "#"    # choose: mark as used
        found = False
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dfs(nr, nc, k + 1):
                found = True
                break
        board[r][c] = saved                  # unchoose: restore (even when found)
        return found

    return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))


def main() -> None:
    board = [list("ABCE"), list("SFCS"), list("ADEE")]
    for w in ["ABCCED", "SEE", "ABCB", "A", "ESCCBA", "ABCESEEDAS"]:
        print(f"solve(board, {w!r:14}) -> {solve(board, w)}")
    print("board restored after search:", board == [list("ABCE"), list("SFCS"), list("ADEE")])
    # Adversarial case: a sea of A's and a single B that the word ends with.
    grid = [["A"] * 4 for _ in range(4)]
    grid[3][3] = "B"
    word = "A" * 9 + "B"
    a: dict = {}
    b: dict = {}
    r1 = brute_force([row[:] for row in grid], word, a)
    r2 = solve([row[:] for row in grid], word, b)
    print(f"adversarial word {word!r}: brute={r1} solve={r2}")
    print("reversing to start from the rare letter makes fewer calls:", b["calls"] < a["calls"])
    print("missing letter is rejected without any DFS:",
          solve([row[:] for row in grid], "AAC", stats := {}) is False and stats == {})


if __name__ == "__main__":
    main()
