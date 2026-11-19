"""
Exercise 02 — Matrix and Character-Grid Reader               [Tier: ★ Core]
Chapter 04 · Pattern: readline injection, grid parsing · Target time: 12 min

Problem
-------
Standard input holds two blocks:

1. "R C" then R lines of C integers (an integer matrix);
2. "H W" then H lines of exactly W characters from {'.', '#'} (a grid).

Write ``read_matrix(readline)`` and ``read_grid(readline)``. Each takes a
zero-argument function that returns the next line (``sys.stdin.readline`` in
production, ``io.StringIO(text).readline`` in tests) and returns
list[list[int]] / list[str]. Raise ValueError on a row of the wrong width.
Then print row sums, column sums, the transpose, and the number of '#' cells.

Examples
--------
>>> import io
>>> read_matrix(io.StringIO("2 3\\n1 2 3\\n4 5 6\\n").readline)
[[1, 2, 3], [4, 5, 6]]
>>> read_grid(io.StringIO("2 3\\r\\n.#.\\r\\n##.").readline)   # CRLF, no final newline
['.#.', '##.']
>>> transpose([[1, 2, 3], [4, 5, 6]])
[[1, 4], [2, 5], [3, 6]]

Constraints
-----------
- 0 <= R, C, H, W <= 1000. Lines may end in "\\n", "\\r\\n", or (last line) nothing.

Hints
-----
- Read the header with ``map(int, readline().split())``.
- ``strip()`` removes "\\n", "\\r\\n" or nothing; ``[:-1]`` does not.
- Validate each row's width and raise ValueError with the row index.
- ``zip(*matrix)`` walks columns.

Follow-ups
----------
- Grid rows that may legitimately contain spaces? Use ``rstrip("\\r\\n")``, not ``strip()``.
- Need a mutable grid? ``[list(row) for row in grid]``.
- Wrong-but-tempting: ``[[0] * C] * R`` to pre-allocate — all R rows alias one list (→ §7.3).
- Columns via ``zip(*matrix)`` yield tuples; wrap in ``list`` if you mutate them.
"""
from __future__ import annotations

import sys
from collections.abc import Callable

Readline = Callable[[], str]


def read_matrix(readline: Readline) -> list[list[int]]:
    raise NotImplementedError("TODO")


def read_grid(readline: Readline) -> list[str]:
    raise NotImplementedError("TODO")


def read_grid_naive(readline: Readline) -> list[str]:
    """Rung 1 (buggy on purpose): line[:-1] assumes every line ends in exactly '\\n'."""
    raise NotImplementedError("TODO")


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def main() -> None:
    readline = sys.stdin.readline
    matrix = read_matrix(readline)
    grid = read_grid(readline)
    print("matrix:", matrix)
    print("row sums:", [sum(row) for row in matrix])
    print("col sums:", [sum(col) for col in zip(*matrix)])
    print("transpose:", transpose(matrix))
    print("grid:", grid)
    print("'#' cells:", sum(row.count("#") for row in grid))

    import io
    crlf = "2 3\r\n.#.\r\n##."
    print("strip() reader on CRLF text:", read_grid(io.StringIO(crlf).readline))
    print("[:-1] reader on CRLF text:  ", read_grid_naive(io.StringIO(crlf).readline))


if __name__ == "__main__":
    main()
