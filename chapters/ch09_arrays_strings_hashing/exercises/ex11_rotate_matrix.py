"""
Exercise 11 — Rotate a Square Matrix 90° Clockwise        [Tier: ★ Core]
Chapter 09 · Pattern: in-place matrix transforms · Target time: 15 min

Problem
-------
Rotate an n x n matrix 90 degrees clockwise in place (do not allocate another
n x n matrix). Return the same matrix object for convenience.

Examples
--------
>>> solve([[1, 2], [3, 4]])
[[3, 1], [4, 2]]

Constraints
-----------
- 0 <= n <= 100; the matrix is square.

Hints
-----
- Where does cell (r, c) go after a clockwise quarter turn?
- Can the rotation be split into two simpler in-place reflections?
- rotate_layers: each move touches four cells at once.

Follow-ups
----------
- Counter-clockwise (rotate_ccw) and 180°: which reflections compose to each?
- Non-square m x n: in-place is impossible in general; return a new n x m matrix.
"""
from __future__ import annotations


def brute_force(matrix: list[list[int]]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def solve(matrix: list[list[int]]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def rotate_layers(matrix: list[list[int]]) -> list[list[int]]:
    """Four-way cycle per ring: top <- left <- bottom <- right <- top."""
    raise NotImplementedError("TODO")


def rotate_ccw(matrix: list[list[int]]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def show(m: list[list[int]]) -> str:
    return "\n".join("  " + " ".join(f"{x:>2}" for x in row) for row in m)


def main() -> None:
    m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    print("original:\n" + show(m))
    print("clockwise:\n" + show(solve([row[:] for row in m])))
    print("counter-clockwise:\n" + show(rotate_ccw([row[:] for row in m])))
    big = [[r * 4 + c for c in range(4)] for r in range(4)]
    agree = solve([r[:] for r in big]) == brute_force([r[:] for r in big]) == rotate_layers([r[:] for r in big])
    print("4x4 methods agree:", agree)
    print("empty:", solve([]), " 1x1:", solve([[7]]))


if __name__ == "__main__":
    main()
