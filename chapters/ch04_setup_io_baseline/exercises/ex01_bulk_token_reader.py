"""
Exercise 01 — Bulk Token Reader for Multiple Test Cases      [Tier: ★ Core]
Chapter 04 · Pattern: fast stdin, token iterator · Target time: 10 min

Problem
-------
Standard input starts with T, the number of test cases. Each case is an integer
n followed by n integers. The judge promises nothing about line breaks: a case
may sit on one line, or its numbers may wrap across several lines.
For each case print one line "Case #k: <sum> <max>", where <max> is "-" when n == 0.

Write ``solve(data: bytes) -> str`` that returns the whole output (no trailing
newline). ``main()`` reads all of stdin and writes the answer.

Examples
--------
>>> solve(b"2\\n3 1 2 3\\n1 -5\\n")
'Case #1: 6 3\\nCase #2: -5 -5'
>>> solve(b"1\\n4 1\\n2\\n3 4\\n")      # numbers wrap across lines
'Case #1: 10 4'
>>> solve(b"1\\n0\\n")
'Case #1: 0 -'

Constraints
-----------
- 0 <= T, total numbers up to 10**6; integers may be negative.
- Lines may end in "\\n" or "\\r\\n" (CRLF test files on a Linux judge, or raw
  sys.stdin.buffer bytes); extra blank lines may appear.

Hints
-----
- ``data.split()`` with no argument splits on any run of whitespace, \\r\\n included.
- Wrap the tokens in ``iter(...)`` and call ``int(next(it))`` each time you need a number.
- ``int()`` accepts bytes: ``int(b"-5") == -5``.
- For ``solve_lines``: ``n, *nums = map(int, readline().split())``.

Follow-ups
----------
- Input too large for memory? Read in chunks or line by line instead.
- Need strings, not ints? ``tok.decode()``; bytes compare unequal to str.
- Want a reusable helper? ``it = iter(data.split()); read = lambda: int(next(it))``.
- Wrong-but-tempting: ``line.split(" ")`` yields '' tokens on double spaces and
  keeps the trailing "\\r\\n"; use ``split()`` with no argument.
"""
from __future__ import annotations

import io
import sys
from collections.abc import Callable, Iterator


def tokens(data: bytes) -> Iterator[bytes]:
    """Whitespace-separated tokens of the whole input, in order."""
    raise NotImplementedError("TODO")


def _case_line(k: int, nums: list[int]) -> str:
    raise NotImplementedError("TODO")


def solve_lines(readline: Callable[[], str]) -> str:
    """Rung 2: line-based. Assumes 'T' on one line and each case on one line."""
    raise NotImplementedError("TODO")


def solve(data: bytes) -> str:
    """Rung 3: bulk read + token iterator; independent of line layout."""
    raise NotImplementedError("TODO")


def main() -> None:
    data = sys.stdin.buffer.read()
    answer = solve(data)
    sys.stdout.write(answer + "\n")
    # Same input through the line-based reader (this input keeps one case per line).
    line_answer = solve_lines(io.StringIO(data.decode()).readline)
    print(f"line-based reader agrees: {line_answer == answer}")
    wrapped = b"1\n4 1\n2\n3 4\n"
    print(f"wrapped case, bulk reader: {solve(wrapped)}")
    try:
        solve_lines(io.StringIO(wrapped.decode()).readline)
    except ValueError as exc:
        print(f"wrapped case, line reader: ValueError: {exc}")


if __name__ == "__main__":
    main()
