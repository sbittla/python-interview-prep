"""
Exercise 12 — Sudoku solver                        [Tier: ◆ Extended]
Chapter 18 · Pattern: constraint backtracking + most-constrained-cell heuristic · Target time: 35 min

Problem
-------
A 9 x 9 Sudoku grid is given as 9 strings of 9 characters, digits '1'-'9' or '.' for empty.
Fill the empty cells so that every row, column and 3 x 3 box contains the digits 1-9 exactly once.
Return the solved grid (as 9 strings) or None if the puzzle has no solution. Do not modify the
input.

Examples
--------
>>> solve(PUZZLE)[0]
'534678912'

Constraints
-----------
- The input is a 9 x 9 grid; given digits may already conflict (then return None).

Hints
-----
- Same template as N-Queens: slots = empty cells, values = digits, constraints = row/col/box.
- Keep a set of used digits for every row, column and box -> O(1) validity checks.
- Box index of (r, c) is (r // 3) * 3 + c // 3.
- Heuristic: always fill the empty cell with the FEWEST legal digits next ("minimum remaining
  values"). A cell with 0 options means backtrack immediately; a cell with 1 option is forced.

Approach ladder
---------------
1. Brute force — fill empty cells in reading order, testing digits 1-9 by scanning the row,
   column and box each time (O(27) per test). Correct, but explores many dead branches.
2. Improved   — the same order with row/col/box sets: O(1) tests, same tree.
3. Optimal-in-practice — sets + most-constrained cell first. The tree shrinks by orders of
   magnitude on hard puzzles. (Exact worst case is still exponential: Sudoku is NP-complete
   for general n.)

Follow-ups
----------
- Count solutions and report whether the puzzle is uniquely solvable (stop after two).
- Constraint propagation (naked singles / hidden singles) before searching.
- Exact cover / Dancing Links (Algorithm X) — the production-grade approach.
"""
from __future__ import annotations

PUZZLE = [
    "53..7....",
    "6..195...",
    ".98....6.",
    "8...6...3",
    "4..8.3..1",
    "7...2...6",
    ".6....28.",
    "...419..5",
    "....8..79",
]

HARD = [  # a puzzle with only 17 givens: plain reading-order backtracking struggles here
    "........1",
    ".......23",
    "..4..5...",
    "...1.....",
    "....3.6..",
    "..7...58.",
    "....67...",
    ".1...4...",
    "52.......",
]


def _box(r: int, c: int) -> int:
    return (r // 3) * 3 + c // 3


def brute_force(grid: list[str], stats: dict | None = None,
                node_limit: int | None = None) -> list[str] | None:
    """Reading-order backtracking with full scans. Returns None also when node_limit is hit."""
    g = [list(row) for row in grid]
    empties = [(r, c) for r in range(9) for c in range(9) if g[r][c] == "."]
    calls = 0

    def ok(r: int, c: int, d: str) -> bool:
        if any(g[r][j] == d for j in range(9)) or any(g[i][c] == d for i in range(9)):
            return False
        br, bc = r - r % 3, c - c % 3
        return all(g[i][j] != d for i in range(br, br + 3) for j in range(bc, bc + 3))

    def backtrack(k: int) -> bool:
        nonlocal calls
        calls += 1
        if node_limit is not None and calls > node_limit:
            raise TimeoutError
        if k == len(empties):
            return True
        r, c = empties[k]
        for d in "123456789":
            if ok(r, c, d):
                g[r][c] = d
                if backtrack(k + 1):
                    return True
                g[r][c] = "."
        return False

    try:
        found = backtrack(0)
    except TimeoutError:
        found = False
    if stats is not None:
        stats["calls"] = calls
    return ["".join(row) for row in g] if found else None


def solve(grid: list[str], stats: dict | None = None) -> list[str] | None:
    g = [list(row) for row in grid]
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empties = []
    for r in range(9):
        for c in range(9):
            d = g[r][c]
            if d == ".":
                empties.append((r, c))
            elif d in rows[r] or d in cols[c] or d in boxes[_box(r, c)]:
                return None                  # the givens already conflict
            else:
                rows[r].add(d); cols[c].add(d); boxes[_box(r, c)].add(d)
    digits = set("123456789")
    calls = 0

    def backtrack() -> bool:
        nonlocal calls
        calls += 1
        if not empties:
            return True
        # Most-constrained cell first (minimum remaining values).
        best_i, best_opts = -1, None
        for i, (r, c) in enumerate(empties):
            opts = digits - rows[r] - cols[c] - boxes[_box(r, c)]
            if best_opts is None or len(opts) < len(best_opts):
                best_i, best_opts = i, opts
                if len(opts) <= 1:
                    break                    # cannot do better than 0 or 1 options
        r, c = empties[best_i]
        empties[best_i] = empties[-1]        # O(1) removal: swap with last, pop
        empties.pop()
        b = _box(r, c)
        for d in sorted(best_opts):          # sorted -> deterministic search order
            g[r][c] = d
            rows[r].add(d); cols[c].add(d); boxes[b].add(d)
            if backtrack():
                return True
            rows[r].remove(d); cols[c].remove(d); boxes[b].remove(d)
        g[r][c] = "."
        empties.append((r, c))               # restore the cell list (unchoose)
        empties[best_i], empties[-1] = empties[-1], empties[best_i]
        return False

    found = backtrack()
    if stats is not None:
        stats["calls"] = calls
    return ["".join(row) for row in g] if found else None


def is_valid_solution(grid: list[str]) -> bool:
    full = set("123456789")
    return (all(set(row) == full for row in grid)
            and all({grid[r][c] for r in range(9)} == full for c in range(9))
            and all({grid[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)} == full
                    for br in (0, 3, 6) for bc in (0, 3, 6)))


def _show(grid: list[str]) -> None:
    for r, row in enumerate(grid):
        if r in (3, 6):
            print("    ------+-------+------")
        print("    " + " | ".join(" ".join(row[i:i + 3]) for i in (0, 3, 6)))


def main() -> None:
    print("puzzle:")
    _show(PUZZLE)
    a: dict = {}
    b: dict = {}
    sol_brute = brute_force(PUZZLE, a)
    sol = solve(PUZZLE, b)
    print("solution:")
    _show(sol)
    print("valid:", is_valid_solution(sol), "| same as brute force:", sol == sol_brute)
    print("input untouched:", PUZZLE[0] == "53..7....")
    print("easy puzzle - fewer calls with most-constrained-cell:", b["calls"] < a["calls"])
    h1: dict = {}
    h2: dict = {}
    hard_brute = brute_force(HARD, h1, node_limit=200_000)
    hard = solve(HARD, h2)
    print("hard puzzle (17 givens):")
    print("   reading-order brute force solved within 200,000 calls:", hard_brute is not None)
    print("   MRV solver solved it:", hard is not None and is_valid_solution(hard),
          "| calls under 200,000:", h2["calls"] < 200_000)
    bad = ["55" + PUZZLE[0][2:]] + PUZZLE[1:]
    print("conflicting givens ->", solve(bad))


if __name__ == "__main__":
    main()
