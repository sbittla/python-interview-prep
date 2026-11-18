"""
Exercise 11 — N-Queens                             [Tier: ★ Core]
Chapter 18 · Pattern: constraint backtracking (row by row, O(1) conflict sets) · Target time: 25 min

Problem
-------
Place n queens on an n x n chessboard so that no two share a row, a column or a diagonal.
Return every solution as a list of n strings ('Q' for a queen, '.' for empty), solutions in
lexicographic order of their column choices. Also provide `count(n)` returning only how many
solutions exist.

Examples
--------
>>> solve(4)
[['.Q..', '...Q', 'Q...', '..Q.'], ['..Q.', 'Q...', '...Q', '.Q..']]
>>> count(8)
92

Constraints
-----------
- 1 <= n <= 9 for solve; count should handle n = 12 comfortably.

Hints
-----
- Place exactly one queen per row; the decision at row r is "which column?".
- A square (r, c) is attacked if column c, diagonal r - c, or anti-diagonal r + c is taken.
  Keep three sets so each check is O(1).
- For count(), replace the sets with three integers used as bitmasks.

Approach ladder
---------------
1. Brute force — every permutation of columns (one queen per row and per column for free), then
   test the diagonals: n! candidates, O(n * n!) — 40,320 boards for n = 8.
2. Improved   — row-by-row backtracking that checks the partial board by scanning earlier queens:
   prunes dead prefixes early, but each check costs O(n).
3. Optimal    — the same with column/diagonal sets: O(1) per check; exponential but tiny in
   practice (about 2,000 calls for n = 8). Bitmasks make count() faster still.

Follow-ups
----------
- Return just one solution for large n (there is a constructive O(n) pattern, or use min-conflicts).
- Exploit symmetry: only try columns in the left half of row 0 and double the count.
- N-Queens is the template for any "assign values to slots under constraints" problem (Sudoku,
  graph colouring, scheduling).
"""
from __future__ import annotations

from itertools import permutations


def _render(cols: list[int] | tuple[int, ...]) -> list[str]:
    n = len(cols)
    return ["." * c + "Q" + "." * (n - c - 1) for c in cols]


def brute_force(n: int) -> list[list[str]]:
    boards = []
    for cols in permutations(range(n)):
        if len({r - c for r, c in enumerate(cols)}) == n and \
           len({r + c for r, c in enumerate(cols)}) == n:
            boards.append(_render(cols))
    return boards


def solve(n: int, stats: dict | None = None) -> list[list[str]]:
    result: list[list[str]] = []
    cols_used: set[int] = set()
    diag: set[int] = set()                  # r - c is constant along a "\" diagonal
    anti: set[int] = set()                  # r + c is constant along a "/" diagonal
    placement: list[int] = []               # placement[r] = column of the queen in row r

    def backtrack(r: int) -> None:
        if stats is not None:
            stats["calls"] = stats.get("calls", 0) + 1
        if r == n:
            result.append(_render(placement))
            return
        for c in range(n):
            if c in cols_used or (r - c) in diag or (r + c) in anti:
                continue                    # prune: attacked square
            cols_used.add(c); diag.add(r - c); anti.add(r + c)          # choose
            placement.append(c)
            backtrack(r + 1)                                            # explore
            placement.pop()                                             # unchoose
            cols_used.remove(c); diag.remove(r - c); anti.remove(r + c)

    backtrack(0)
    return result


def count(n: int) -> int:
    full = (1 << n) - 1

    def go(cols: int, diag: int, anti: int) -> int:
        if cols == full:
            return 1
        total = 0
        free = full & ~(cols | diag | anti)  # bit c set = column c is safe in this row
        while free:
            bit = free & -free               # lowest safe column
            free ^= bit
            # diagonals shift by one column as we move down a row
            total += go(cols | bit, ((diag | bit) << 1) & full, (anti | bit) >> 1)
        return total

    return go(0, 0, 0)


def trace(n: int) -> list[str]:
    """Decision tree of solve(n): one line per tried square, marking dead ends and solutions."""
    lines: list[str] = []
    cols_used: set[int] = set()
    diag: set[int] = set()
    anti: set[int] = set()

    def backtrack(r: int) -> None:
        for c in range(n):
            pad = "    " * r
            if c in cols_used or (r - c) in diag or (r + c) in anti:
                lines.append(f"{pad}row {r} col {c}: attacked")
                continue
            lines.append(f"{pad}row {r} col {c}: place" + ("  => SOLUTION" if r == n - 1 else ""))
            cols_used.add(c); diag.add(r - c); anti.add(r + c)
            backtrack(r + 1)
            cols_used.remove(c); diag.remove(r - c); anti.remove(r + c)

    backtrack(0)
    return lines


def main() -> None:
    sols = solve(4)
    print("n=4 has", len(sols), "solutions:")
    for board in sols:
        for row in board:
            print("   ", row)
        print()
    print("solve(4) == brute_force(4):", sols == brute_force(4))
    print("counts n=1..10:", [count(n) for n in range(1, 11)])
    print("count(12) =", count(12))
    stats: dict = {}
    solve(8, stats)
    print("n=8: brute force tests 40320 permutations; backtracking makes", stats["calls"], "calls")
    print("decision tree for n=4 (first solution branch and its dead ends):")
    lines = trace(4)
    stop = next(i for i, line in enumerate(lines) if "SOLUTION" in line)
    for line in lines[:stop + 1]:
        print("  " + line)


if __name__ == "__main__":
    main()
