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

Approach ladder
---------------
1. Brute force — new matrix: new[c][n-1-r] = old[r][c]. O(n^2) time and
   O(n^2) extra space. One-liner: [list(row) for row in zip(*matrix[::-1])].
2. Optimal    — transpose in place (swap across the main diagonal), then reverse
   each row. O(n^2) time, O(1) extra space.
3. Alternative optimal — rotate four cells at a time, ring by ring. Same
   complexity; more index arithmetic, so more bug-prone under pressure.

Follow-ups
----------
- Counter-clockwise: transpose then reverse each column (or reverse rows first).
- 180°: reverse rows and reverse each row.
- Non-square m x n: in-place is impossible in general; return a new n x m matrix.
"""
from __future__ import annotations


def brute_force(matrix: list[list[int]]) -> list[list[int]]:
    rotated = [list(row) for row in zip(*matrix[::-1])]
    matrix[:] = rotated
    return matrix


def solve(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    for r in range(n):                       # 1) transpose
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    for row in matrix:                       # 2) mirror left-right
        row.reverse()
    return matrix


def rotate_layers(matrix: list[list[int]]) -> list[list[int]]:
    """Four-way cycle per ring: top <- left <- bottom <- right <- top."""
    n = len(matrix)
    for layer in range(n // 2):
        first, last = layer, n - 1 - layer
        for i in range(first, last):
            off = i - first
            top = matrix[first][i]
            matrix[first][i] = matrix[last - off][first]
            matrix[last - off][first] = matrix[last][last - off]
            matrix[last][last - off] = matrix[i][last]
            matrix[i][last] = top
    return matrix


def rotate_ccw(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    matrix.reverse()                         # transpose, then flip upside down
    return matrix


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
