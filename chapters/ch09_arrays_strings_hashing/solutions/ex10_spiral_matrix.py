"""
Exercise 10 — Spiral Order and Diagonals                  [Tier: ★ Core]
Chapter 09 · Pattern: matrix traversal with shrinking bounds · Target time: 20 min

Problem
-------
Given an m x n matrix (list of rows), return its elements in clockwise spiral
order starting at the top-left. Also implement diagonals(matrix): group the
cells by anti-diagonal r + c, each group listed top-to-bottom.

Examples
--------
>>> solve([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
[1, 2, 3, 6, 9, 8, 7, 4, 5]
>>> diagonals([[1, 2], [3, 4]])
[[1], [2, 3], [4]]

Constraints
-----------
- 0 <= m, n <= 100; rows all have length n.

Approach ladder
---------------
1. Simulation with a visited grid — walk, turn right when the next cell is out
   of range or visited. O(mn) time, O(mn) extra space.
2. Optimal    — four shrinking boundaries top/bottom/left/right; peel one ring
   per loop. O(mn) time, O(1) extra space. The guards before the bottom row and
   the left column are what handle single-row / single-column leftovers.

Follow-ups
----------
- Generate an n x n spiral matrix of 1..n^2 (same boundaries, write instead of read).
- Counter-clockwise or starting elsewhere: change the order of the four legs.
- Main diagonals (r - c constant) vs anti-diagonals (r + c constant).
"""
from __future__ import annotations


def brute_force(matrix: list[list[int]]) -> list[int]:
    if not matrix or not matrix[0]:
        return []
    m, n = len(matrix), len(matrix[0])
    seen = [[False] * n for _ in range(m)]
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]        # right, down, left, up
    r = c = d = 0
    out = []
    for _ in range(m * n):
        out.append(matrix[r][c])
        seen[r][c] = True
        nr, nc = r + dirs[d][0], c + dirs[d][1]
        if not (0 <= nr < m and 0 <= nc < n) or seen[nr][nc]:
            d = (d + 1) % 4
            nr, nc = r + dirs[d][0], c + dirs[d][1]
        r, c = nr, nc
    return out


def solve(matrix: list[list[int]]) -> list[int]:
    out: list[int] = []
    if not matrix or not matrix[0]:
        return out
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):            # top row, left -> right
            out.append(matrix[top][c])
        for r in range(top + 1, bottom + 1):        # right column, down
            out.append(matrix[r][right])
        if top < bottom:                            # bottom row, right -> left
            for c in range(right - 1, left - 1, -1):
                out.append(matrix[bottom][c])
        if left < right:                            # left column, up
            for r in range(bottom - 1, top, -1):
                out.append(matrix[r][left])
        top, bottom, left, right = top + 1, bottom - 1, left + 1, right - 1
    return out


def diagonals(matrix: list[list[int]]) -> list[list[int]]:
    if not matrix or not matrix[0]:
        return []
    m, n = len(matrix), len(matrix[0])
    groups: list[list[int]] = [[] for _ in range(m + n - 1)]
    for r in range(m):
        for c in range(n):
            groups[r + c].append(matrix[r][c])
    return groups


def main() -> None:
    grids = {
        "3x3": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        "3x4": [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
        "1x3": [[1, 2, 3]],
        "3x1": [[1], [2], [3]],
        "empty": [],
    }
    for name, g in grids.items():
        print(f"{name:<5} spiral={solve(g)}  same_as_sim={solve(g) == brute_force(g)}")
    print("columns of 3x4:", [list(col) for col in zip(*grids["3x4"])])
    print("anti-diagonals 3x3:", diagonals(grids["3x3"]))
    print("main diagonal 3x3:", [grids["3x3"][i][i] for i in range(3)])


if __name__ == "__main__":
    main()
