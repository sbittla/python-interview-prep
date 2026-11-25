"""
Exercise 03 — Grid Paths: Obstacles and Minimum Path Sum            [Tier: ★ Core]
Chapter 19 · Pattern: 2D grid DP, rolling row · Target time: 25 min

Problem
-------
A robot starts at the top-left cell of an m x n grid and may only move right (R) or
down (D) until it reaches the bottom-right cell.
1. `unique_paths(grid)` — grid cells are 0 (free) or 1 (rock). Count the paths that
   avoid rocks. A rock on the start or finish means 0 paths.
2. `min_path_sum(grid)` — cells hold non-negative costs; return the smallest total of
   the cells on a path (start and finish included).
3. `min_path(grid)` — the same total plus one optimal move string such as "RRDD".

Examples
--------
>>> unique_paths([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
2
>>> min_path([[1, 3, 1], [1, 5, 1], [4, 2, 1]])
(7, 'RRDD')

Constraints
-----------
- 1 <= m, n <= 200; every row has length n.

Approach ladder
---------------
DP recipe (unique_paths) — state: ways(r, c) = paths from the start to (r, c);
transition: ways(r, c) = ways(r-1, c) + ways(r, c-1), or 0 on a rock; base:
ways(0, 0) = 1 if free; order: row by row, left to right; answer: ways(m-1, n-1).
min_path_sum is the same shape with min(...) + grid[r][c].
1. Plain recursion — explores every path: O(2^(m+n)) time, O(m+n) stack.
2. Memoised — m*n states, O(1) each: O(mn) time, O(mn) space.
3. Bottom-up table — O(mn) time, O(mn) space; needed to reconstruct the path.
4. Rolling row — a cell reads the row above and the cell to its left, so one row of
   length n suffices: O(mn) time, O(n) space (use the shorter side as the row).

Hints
-----
- The first row and first column have only one way in; a rock cuts everything after it.
- In the rolling row, row[c] still holds "above" before you overwrite it, and
  row[c - 1] already holds "left".
- Reconstruct backwards from the finish: step to whichever neighbour (up or left)
  produced the minimum.

Follow-ups
----------
- Without rocks the count is C(m+n-2, m-1) (`math.comb`).
- Allow up/left moves too: states now depend on each other in cycles, so no fill order
  exists; min path sum becomes Dijkstra (Ch 16), counting simple paths backtracking (Ch 18).
"""
from __future__ import annotations

from functools import cache


# ---------------------------------------------------------------- unique paths
def unique_paths_brute(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])

    def ways(r: int, c: int) -> int:            # paths from (r, c) to the finish
        if r >= m or c >= n or grid[r][c]:
            return 0
        if (r, c) == (m - 1, n - 1):
            return 1
        return ways(r + 1, c) + ways(r, c + 1)

    return ways(0, 0)


def unique_paths_memo(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])

    @cache
    def ways(r: int, c: int) -> int:
        if r >= m or c >= n or grid[r][c]:
            return 0
        if (r, c) == (m - 1, n - 1):
            return 1
        return ways(r + 1, c) + ways(r, c + 1)

    return ways(0, 0)


def unique_paths_table(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])
    ways = [[0] * n for _ in range(m)]
    for r in range(m):
        for c in range(n):
            if grid[r][c]:
                continue
            if r == c == 0:
                ways[r][c] = 1
            else:
                ways[r][c] = (ways[r - 1][c] if r else 0) + (ways[r][c - 1] if c else 0)
    return ways[-1][-1]


def unique_paths(grid: list[list[int]]) -> int:
    n = len(grid[0])
    row = [1] + [0] * (n - 1)                   # a virtual "1 way" above the start
    for cells in grid:
        for c in range(n):
            if cells[c]:
                row[c] = 0
            elif c:
                row[c] += row[c - 1]            # above (old row[c]) + left (new row[c-1])
    return row[-1]


# ---------------------------------------------------------------- min path sum
def min_path_sum_brute(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])

    def cost(r: int, c: int) -> float:          # cheapest from (r, c) to the finish
        if r >= m or c >= n:
            return float("inf")
        if (r, c) == (m - 1, n - 1):
            return grid[r][c]
        return grid[r][c] + min(cost(r + 1, c), cost(r, c + 1))

    return int(cost(0, 0))


def min_path_sum_memo(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])

    @cache
    def cost(r: int, c: int) -> float:
        if r >= m or c >= n:
            return float("inf")
        if (r, c) == (m - 1, n - 1):
            return grid[r][c]
        return grid[r][c] + min(cost(r + 1, c), cost(r, c + 1))

    return int(cost(0, 0))


def _min_table(grid: list[list[int]]) -> list[list[int]]:
    m, n = len(grid), len(grid[0])
    best = [[0] * n for _ in range(m)]
    for r in range(m):
        for c in range(n):
            if r == c == 0:
                best[r][c] = grid[0][0]
            elif r == 0:
                best[r][c] = best[r][c - 1] + grid[r][c]
            elif c == 0:
                best[r][c] = best[r - 1][c] + grid[r][c]
            else:
                best[r][c] = min(best[r - 1][c], best[r][c - 1]) + grid[r][c]
    return best


def min_path_sum_table(grid: list[list[int]]) -> int:
    return _min_table(grid)[-1][-1]


def min_path_sum(grid: list[list[int]]) -> int:
    inf = float("inf")
    row = [inf] * len(grid[0])
    row[0] = 0                                  # virtual 0 above the start
    for cells in grid:
        row[0] += cells[0]
        for c in range(1, len(cells)):
            row[c] = min(row[c], row[c - 1]) + cells[c]
    return int(row[-1])


def min_path(grid: list[list[int]]) -> tuple[int, str]:
    best = _min_table(grid)
    r, c, moves = len(grid) - 1, len(grid[0]) - 1, []
    while (r, c) != (0, 0):
        if r and (c == 0 or best[r - 1][c] <= best[r][c - 1]):
            moves.append("D")
            r -= 1
        else:
            moves.append("R")
            c -= 1
    return best[-1][-1], "".join(reversed(moves))


def main() -> None:
    rocks = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    for g in (rocks, [[0, 1], [0, 0]], [[1]], [[0] * 7 for _ in range(3)],
              [[0, 0], [1, 1], [0, 0]]):
        rungs = (unique_paths_brute(g), unique_paths_memo(g), unique_paths_table(g),
                 unique_paths(g))
        print(f"unique_paths {g} = {rungs[-1]}  rungs agree: {len(set(rungs)) == 1}")
    for g in ([[1, 3, 1], [1, 5, 1], [4, 2, 1]], [[1, 2, 3], [4, 5, 6]], [[5]]):
        rungs = (min_path_sum_brute(g), min_path_sum_memo(g), min_path_sum_table(g),
                 min_path_sum(g))
        print(f"min_path {g} = {min_path(g)}  rungs agree: {len(set(rungs)) == 1}")


if __name__ == "__main__":
    main()
