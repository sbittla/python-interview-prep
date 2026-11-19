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
- Allow up/left moves too: cycles appear and DP no longer applies; use Dijkstra (Ch 16).
"""
from __future__ import annotations

from functools import cache


# ---------------------------------------------------------------- unique paths
def unique_paths_brute(grid: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def unique_paths_memo(grid: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def unique_paths_table(grid: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def unique_paths(grid: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


# ---------------------------------------------------------------- min path sum
def min_path_sum_brute(grid: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def min_path_sum_memo(grid: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def _min_table(grid: list[list[int]]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def min_path_sum_table(grid: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def min_path_sum(grid: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def min_path(grid: list[list[int]]) -> tuple[int, str]:
    raise NotImplementedError("TODO")


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
