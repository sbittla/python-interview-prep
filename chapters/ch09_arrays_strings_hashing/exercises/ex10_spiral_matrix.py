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

Hints
-----
- Keep four boundaries: top, bottom, left, right.
- Per loop: top row, right column, bottom row (if top < bottom), left column (if left < right); then shrink.
- Anti-diagonals: cells with the same r + c belong together.

Follow-ups
----------
- Generate an n x n spiral matrix of 1..n^2 (same boundaries, write instead of read).
- Counter-clockwise or starting elsewhere: change the order of the four legs.
- Main diagonals (r - c constant) vs anti-diagonals (r + c constant).
"""
from __future__ import annotations


def brute_force(matrix: list[list[int]]) -> list[int]:
    raise NotImplementedError("TODO")


def solve(matrix: list[list[int]]) -> list[int]:
    raise NotImplementedError("TODO")


def diagonals(matrix: list[list[int]]) -> list[list[int]]:
    raise NotImplementedError("TODO")


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
