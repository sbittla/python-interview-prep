"""
Exercise 03 — Grid Rows That Move Together              [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (references) · Target time: 5 min

Problem
-------
`make_grid(rows, cols, fill)` must build a rows x cols grid (list of lists) whose
rows are independent: setting `grid[0][0]` must change only that one cell. The
buggy version uses `[[fill] * cols] * rows`, which repeats a reference to the
SAME inner list `rows` times.

Examples
--------
>>> g = solve(3, 2, 0)
>>> g[0][0] = 9
>>> g
[[9, 0], [0, 0], [0, 0]]

Constraints
-----------
- 0 <= rows, cols <= 1000
- `fill` is an immutable value (int, str, None, ...).

Approach ladder
---------------
1. Buggy  — `[[fill] * cols] * rows`: outer `*` copies references, not rows.
2. Fixed  — a comprehension builds a new inner list per row:
   `[[fill] * cols for _ in range(rows)]`. O(rows*cols) time and space.

Follow-ups
----------
- Why is the inner `[fill] * cols` safe? (`fill` is immutable; rebinding a cell
  replaces the reference instead of mutating a shared object.)
- What about `[[[]] * cols for _ in range(rows)]`? (Cells share one list — same bug, one level down.)
"""
from __future__ import annotations

from typing import Any


def buggy_make_grid(rows: int, cols: int, fill: Any = 0) -> list[list[Any]]:
    return [[fill] * cols] * rows


def solve(rows: int, cols: int, fill: Any = 0) -> list[list[Any]]:
    """Build a grid whose rows are distinct list objects."""
    return [[fill] * cols for _ in range(rows)]


def main() -> None:
    g = buggy_make_grid(3, 2)
    g[0][0] = 9
    print("buggy grid after g[0][0] = 9:", g)
    print("buggy distinct rows:", len({id(r) for r in g}))
    g = solve(3, 2)
    g[0][0] = 9
    print("fixed grid after g[0][0] = 9:", g)
    print("fixed distinct rows:", len({id(r) for r in g}))
    print("empty grid:", solve(0, 5))


if __name__ == "__main__":
    main()
