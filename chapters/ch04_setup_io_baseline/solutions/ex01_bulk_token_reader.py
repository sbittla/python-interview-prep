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

Approach ladder
---------------
1. Brute force — ``input()`` per line, assuming each case is exactly one line.
   O(total) work, but each ``input()`` call has overhead, and the code breaks
   as soon as a case wraps or a blank line appears.
2. Improved   — ``sys.stdin.readline`` (``solve_lines``): same logic, several
   times faster per line, still layout-dependent.
3. Optimal    — read everything once (``sys.stdin.buffer.read()``), ``split()``
   into byte tokens, and pull them with ``next(it)``. One system read,
   O(total) time and memory, and line layout no longer matters because
   ``split()`` with no argument treats spaces, tabs, \\n and \\r\\n alike.
   ``int()`` accepts bytes directly, so no ``decode()`` is needed.

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
    return iter(data.split())


def _case_line(k: int, nums: list[int]) -> str:
    return f"Case #{k}: {sum(nums)} {max(nums) if nums else '-'}"


def solve_lines(readline: Callable[[], str]) -> str:
    """Rung 2: line-based. Assumes 'T' on one line and each case on one line."""
    t = int(readline())
    out = []
    for k in range(1, t + 1):
        n, *nums = map(int, readline().split())
        if len(nums) != n:
            raise ValueError(f"case {k}: expected {n} numbers on one line, got {len(nums)}")
        out.append(_case_line(k, nums))
    return "\n".join(out)


def solve(data: bytes) -> str:
    """Rung 3: bulk read + token iterator; independent of line layout."""
    it = tokens(data)
    t = int(next(it, b"0"))
    out = []
    for k in range(1, t + 1):
        n = int(next(it))
        nums = [int(next(it)) for _ in range(n)]
        out.append(_case_line(k, nums))
    return "\n".join(out)


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
