"""
Exercise 11 — Range-Sum Queries in 1D and 2D             [Tier: ★ Core]
Chapter 10 · Pattern: prefix sums (1D and 2D, inclusion-exclusion) · Target time: 20 min

Problem
-------
Build an immutable structure over a grid of integers that answers many
queries sum_region(r1, c1, r2, c2): the sum of grid[r][c] for
r1 <= r <= r2 and c1 <= c <= c2 (inclusive corners). RangeSum1D does the same
for a list with sum_range(i, j), inclusive.

Examples
--------
>>> g = [[3, 0, 1], [5, 6, 3], [1, 2, 0]]
>>> NumMatrix(g).sum_region(1, 1, 2, 2)          # 6 + 3 + 2 + 0
11
>>> RangeSum1D([-2, 0, 3, -5, 2, -1]).sum_range(2, 5)
-1

Constraints
-----------
- Up to 200 x 200 grid; up to 10**4 queries; 0 <= r1 <= r2 < rows, etc.

Approach ladder
---------------
1. Brute force — sum the rectangle per query. O(r * c) per query, O(1) build.
2. Improved   — a prefix sum per row; a query sums one O(1) difference per
   row. O(r * c) build, O(r) per query.
3. Optimal    — 2D prefix table P with one row and column of zero padding:
       P[i+1][j+1] = grid[i][j] + P[i][j+1] + P[i+1][j] - P[i][j]
   and a query is inclusion-exclusion of four corners:
       P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
   O(r * c) build and space, O(1) per query. Move up a rung when queries
   are many: q * (r * c) quickly dwarfs a one-off O(r * c) build.

Wrong-but-tempting
------------------
- No padding row/column: every query needs special cases for r1 == 0 or
  c1 == 0, and the easy mistake is P[r1-1] wrapping to P[-1] (the LAST row)
  silently in Python.
- Mutable grid with frequent updates: prefix sums need O(r*c) rebuild per
  update; use a Fenwick tree instead (follow-up; -> Chapter 22.9).

Follow-ups
----------
- Point updates + range queries: Fenwick (binary indexed) tree, O(log n)
  (-> Chapter 22.9).
- Range updates instead of queries: difference arrays (ex12).
"""
from __future__ import annotations

from itertools import accumulate


class RangeSum1D:
    def __init__(self, nums: list[int]) -> None:
        self.p = [0, *accumulate(nums)]   # p[i] = sum(nums[:i])

    def sum_range(self, i: int, j: int) -> int:
        return self.p[j + 1] - self.p[i]


class BruteMatrix:
    def __init__(self, grid: list[list[int]]) -> None:
        self.grid = grid

    def sum_region(self, r1: int, c1: int, r2: int, c2: int) -> int:
        return sum(self.grid[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1))


class RowPrefixMatrix:
    def __init__(self, grid: list[list[int]]) -> None:
        self.rows = [[0, *accumulate(row)] for row in grid]

    def sum_region(self, r1: int, c1: int, r2: int, c2: int) -> int:
        return sum(self.rows[r][c2 + 1] - self.rows[r][c1] for r in range(r1, r2 + 1))


class NumMatrix:
    def __init__(self, grid: list[list[int]]) -> None:
        rows, cols = len(grid), len(grid[0]) if grid else 0
        p = [[0] * (cols + 1) for _ in range(rows + 1)]
        for i in range(rows):
            for j in range(cols):
                p[i + 1][j + 1] = grid[i][j] + p[i][j + 1] + p[i + 1][j] - p[i][j]
        self.p = p

    def sum_region(self, r1: int, c1: int, r2: int, c2: int) -> int:
        p = self.p
        return p[r2 + 1][c2 + 1] - p[r1][c2 + 1] - p[r2 + 1][c1] + p[r1][c1]


def main() -> None:
    small = [[3, 0, 1], [5, 6, 3], [1, 2, 0]]
    print(f"grid={small} sum_region(1, 1, 2, 2) -> {NumMatrix(small).sum_region(1, 1, 2, 2)}"
          f"  brute={BruteMatrix(small).sum_region(1, 1, 2, 2)}")
    grid = [[3, 0, 1, 4, 2],
            [5, 6, 3, 2, 1],
            [1, 2, 0, 1, 5],
            [4, 1, 0, 1, 7],
            [1, 0, 3, 0, 5]]
    fast, rows, brute = NumMatrix(grid), RowPrefixMatrix(grid), BruteMatrix(grid)
    for q in [(2, 1, 4, 3), (1, 1, 2, 2), (1, 2, 2, 4), (0, 0, 0, 0), (0, 0, 4, 4)]:
        print(f"sum_region{q} -> {fast.sum_region(*q):<3} row-prefix={rows.sum_region(*q):<3}"
              f" brute={brute.sum_region(*q)}")
    one = RangeSum1D([-2, 0, 3, -5, 2, -1])
    print("1D:", [one.sum_range(i, j) for i, j in [(0, 2), (2, 5), (0, 5), (3, 3)]])


if __name__ == "__main__":
    main()
