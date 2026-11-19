"""
Exercise 04 — Output Formatting and Fast Writing             [Tier: ★ Core]
Chapter 04 · Pattern: build once, write once · Target time: 10 min

Problem
-------
Judges compare output byte-for-byte (usually ignoring trailing whitespace).
Write the helpers a solution needs to print answers correctly and fast:

- ``format_row(values)``      -> "1 2 3" (space-separated, no trailing space)
- ``format_cases(answers)``   -> "Case #1: a\\nCase #2: b" (1-based)
- ``format_float(x, places)`` -> fixed decimals, and never "-0.000"
- ``format_bool(flag)``       -> "YES" / "NO"
- ``write_lines(lines, out)`` -> one ``out.write`` call; writes nothing for no lines

Examples
--------
>>> format_row([1, 2, 3])
'1 2 3'
>>> format_cases(["YES", 7])
'Case #1: YES\\nCase #2: 7'
>>> format_float(2 / 3, 3)
'0.667'
>>> format_float(-0.0001, 2)
'0.00'
>>> format_bool(False)
'NO'

Constraints
-----------
- Up to 10**6 output lines; ``out`` is any object with ``write`` (sys.stdout, StringIO).

Hints
-----
- ``" ".join(map(str, values))`` and ``"\\n".join(...)`` build output in O(total length).
- ``f"{x:.{places}f}"`` formats with a variable number of decimals.
- If the formatted string parses to 0.0, re-format 0.0 to avoid "-0.00".
- ``"\\n".join([])`` is ""; don't write a lone newline in that case.

Follow-ups
----------
- Must values be rounded or truncated? Ask; ``f"{x:.2f}"`` rounds the exact
  binary value, and 2.675 is stored as 2.67499..., so it prints 2.67.
- Interactive problems: flush after each answer (``print(..., flush=True)``);
  batching output there causes a hang.
- Wrong-but-tempting: ``print(*values)`` is fine for one row, but ``print(values)``
  prints the list brackets.
"""
from __future__ import annotations

import io
import sys
from collections.abc import Iterable
from typing import TextIO


def format_row(values: Iterable[object]) -> str:
    raise NotImplementedError("TODO")


def format_cases(answers: Iterable[object]) -> str:
    raise NotImplementedError("TODO")


def format_float(x: float, places: int = 6) -> str:
    raise NotImplementedError("TODO")


def format_bool(flag: bool) -> str:
    raise NotImplementedError("TODO")


def write_lines(lines: Iterable[str], out: TextIO) -> None:
    raise NotImplementedError("TODO")


def print_loop(lines: Iterable[str], out: TextIO) -> None:
    """Rung 1: one print() per line (correct, slower)."""
    raise NotImplementedError("TODO")


def main() -> None:
    lines = [format_row(range(1, 6)),
             format_cases(["YES", 42]),
             format_float(2 / 3, 3),
             format_float(-0.0001, 2),
             format_bool(3 > 5)]
    write_lines(lines, sys.stdout)

    a, b = io.StringIO(), io.StringIO()
    many = [str(i * i) for i in range(1000)]
    write_lines(many, a)
    print_loop(many, b)
    print(f"join output equals print-loop output: {a.getvalue() == b.getvalue()}")

    empty = io.StringIO()
    write_lines([], empty)
    print(f"no answers writes: {empty.getvalue()!r}")
    print(f"naive f-string on -0.0001: {-0.0001:.2f}")
    print(f"0.1 + 0.2 printed raw: {0.1 + 0.2}  formatted: {format_float(0.1 + 0.2, 2)}")
    print(f"print(list) vs print(*list): {[1, 2, 3]} | {format_row([1, 2, 3])}")


if __name__ == "__main__":
    main()
