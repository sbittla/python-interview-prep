"""
Exercise 04 — Dry-Run Tracer                                [Tier: ◆ Extended]
Chapter 02 · Pattern: interview method (test by dry run) · Target time: 25 min

Problem
-------
In an interview you test code by "dry running" it: walking a small input line
by line and writing down how each variable changes. Build a tool that produces
exactly that table, so you can check your hand-trace against reality.

trace(func, *args, max_steps=1000) -> (rows, result)

- rows is a list of (line, changes): `line` is the line number RELATIVE to the
  `def` line (def = 0, so output never depends on where the file sits), and
  `changes` is a dict name -> repr(value) of locals that are new or changed
  after that line ran (empty if nothing changed). The first row is
  (0, {arguments}); then one row per executed line.
- result is func's return value.
- Only lines of func itself are traced, not functions it calls.
- More than max_steps line events raises RuntimeError (catches infinite
  loops during a dry run).

render(func, rows) -> list of strings, one per row: step number, relative
line, the stripped source of that line, and the changes as "k=v" pairs.

Examples
--------
>>> rows, result = trace(count_pairs, [2, 2], 4)
>>> rows[0]
(0, {'nums': '[2, 2]', 'target': '4'})
>>> result
1

Constraints
-----------
- Restore any previously installed trace function afterwards, even on error.
- Mutation must be detected (e.g. seen[x] = ... changes `seen`), so snapshot
  locals by repr, not by identity.

Hints
-----
- sys.settrace(global_tracer): on a 'call' event for func.__code__ return a
  local tracer; for any other frame return None (not traced).
- Locals at a 'line' event show the state BEFORE that line runs, so diff the
  new snapshot against the previous one and credit the previous line.
- Snapshot with repr() so in-place mutation (lists, dicts) shows up.
- Restore the old tracer in a finally block.

Follow-ups
----------
- Show the loop iteration number next to each row.
- Trace a recursive function: key rows by frame depth.
"""
from __future__ import annotations

import inspect
import sys
from typing import Any, Callable


def trace(func: Callable[..., Any], *args: Any, max_steps: int = 1000) -> tuple[list, Any]:
    raise NotImplementedError("TODO")


def render(func: Callable[..., Any], rows: list) -> list[str]:
    raise NotImplementedError("TODO")


def count_pairs(nums: list[int], target: int) -> int:
    seen: dict[int, int] = {}
    pairs = 0
    for x in nums:
        pairs += seen.get(target - x, 0)
        seen[x] = seen.get(x, 0) + 1
    return pairs


def spin(n: int) -> int:
    while n != 0:          # bug: never reaches 0 when n is odd or negative
        n -= 2
    return n


def main() -> None:
    rows, result = trace(count_pairs, [1, 3, 2, 2], 4)
    print("Dry run of count_pairs([1, 3, 2, 2], 4):")
    for line in render(count_pairs, rows):
        print(line)
    print(f"result = {result}")
    rows, result = trace(spin, 4)
    print(f"\nspin(4) -> {result} in {len(rows) - 1} traced lines")
    try:
        trace(spin, 3, max_steps=50)
    except RuntimeError as exc:
        print(f"spin(3) -> RuntimeError: {exc}")


if __name__ == "__main__":
    main()
