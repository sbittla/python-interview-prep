"""
Exercise 03 — Sentinel, EOF and Blank-Line Framings          [Tier: ◆ Extended]
Chapter 04 · Pattern: input framing, ragged lines · Target time: 15 min

Problem
-------
Judges frame "many test cases" in four ways: a count first (see ex01), a
sentinel line that ends the input, "read until end of file", and blocks
separated by blank lines. Implement the last three over any iterable of lines
(``sys.stdin``, a list, or ``io.StringIO``):

- ``read_until_sentinel(lines)`` -> list of (a, b) pairs, stopping at "0 0"
  (the sentinel itself is not returned; anything after it is ignored).
- ``read_until_eof(lines)`` -> list of int rows; rows are ragged (any length);
  blank lines are skipped.
- ``read_blocks(lines)`` -> list of blocks, each a list of int rows; one or more
  blank lines end a block; leading/trailing blank lines create no empty block.

``main()`` reads blank-line-separated blocks from stdin and prints, per block,
its row count, its total and its largest row sum.

Examples
--------
>>> read_until_sentinel(["3 4\\n", "10 2\\n", "0 0\\n", "9 9\\n"])
[(3, 4), (10, 2)]
>>> read_until_eof(["1 2 3\\n", "\\n", "4\\n"])
[[1, 2, 3], [4]]
>>> read_blocks(["1 2\\n", "3\\n", "\\n", "\\n", "4\\n"])
[[[1, 2], [3]], [[4]]]

Constraints
-----------
- Lines may end in "\\n", "\\r\\n" or nothing. Whitespace-only lines count as blank.

Approach ladder
---------------
1. Brute force — ``while True: line = input()`` and catch EOFError to stop.
   Works, but mixes control flow with exceptions and is slow per line.
2. Improved   — ``for line in sys.stdin``: iteration simply stops at EOF.
   O(total) time; no exception handling needed.
3. Optimal    — the same loop over an *injected* iterable, plus a "current
   block" buffer that is flushed on a blank line and once more at the end
   (forgetting that final flush is the classic bug). O(total) time and space.

Follow-ups
----------
- Sentinel missing (input just ends)? Stop at EOF too; don't crash.
- Huge input: switch to the bulk token reader (ex01) when framing allows it.
- Wrong-but-tempting: ``text.split("\\n\\n")`` — fails on "\\r\\n\\r\\n" and on
  blank lines that contain spaces.
"""
from __future__ import annotations

import sys
from collections.abc import Iterable


def read_until_sentinel(lines: Iterable[str]) -> list[tuple[int, int]]:
    pairs = []
    for line in lines:
        parts = line.split()
        if not parts:
            continue
        a, b = map(int, parts)
        if a == 0 and b == 0:
            break
        pairs.append((a, b))
    return pairs


def read_until_eof(lines: Iterable[str]) -> list[list[int]]:
    return [list(map(int, line.split())) for line in lines if line.strip()]


def read_blocks(lines: Iterable[str]) -> list[list[list[int]]]:
    blocks: list[list[list[int]]] = []
    current: list[list[int]] = []
    for line in lines:
        if line.strip():
            current.append(list(map(int, line.split())))
        elif current:                      # blank line closes a non-empty block
            blocks.append(current)
            current = []
    if current:                            # the final flush everyone forgets
        blocks.append(current)
    return blocks


def read_blocks_naive(text: str) -> list[list[list[int]]]:
    """Wrong-but-tempting: split on a literal blank line."""
    return [[list(map(int, row.split())) for row in chunk.split("\n") if row]
            for chunk in text.split("\n\n") if chunk]


def main() -> None:
    blocks = read_blocks(sys.stdin)
    for k, block in enumerate(blocks, 1):
        sums = [sum(row) for row in block]
        print(f"block {k}: rows={len(block)} total={sum(sums)} best_row={max(sums)}")

    print("sentinel:", read_until_sentinel(["3 4\n", "10 2\n", "0 0\n", "9 9\n"]))
    print("sentinel missing:", read_until_sentinel(["5 6\n"]))
    print("until EOF:", read_until_eof(["1 2 3\n", "   \n", "4\r\n", "5 6"]))
    crlf = "1 2\r\n3\r\n\r\n4\r\n"
    print("blocks (CRLF):", read_blocks(crlf.splitlines(keepends=True)))
    print("naive split on CRLF:", read_blocks_naive(crlf))


if __name__ == "__main__":
    main()
