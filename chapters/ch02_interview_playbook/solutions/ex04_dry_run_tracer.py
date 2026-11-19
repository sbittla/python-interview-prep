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

Approach ladder
---------------
1. Brute force — add print() after every line by hand. Works, but edits the
   code under test and is slow to undo.
2. Optimal    — sys.settrace with a local tracer: on each 'line' or 'return'
   event, diff a repr snapshot of f_locals against the previous one and
   attribute the diff to the previous line. O(L * V) for L lines, V locals.

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
    code = func.__code__
    first = code.co_firstlineno
    rows: list[tuple[int, dict[str, str]]] = []
    state = {"prev": {}, "line": None, "steps": 0}

    def diff(frame) -> dict[str, str]:
        snap = {k: repr(v) for k, v in frame.f_locals.items()}
        changes = {k: v for k, v in snap.items() if state["prev"].get(k) != v}
        state["prev"] = snap
        return changes

    def local(frame, event, arg):
        if event in ("line", "return"):
            changes = diff(frame)
            if state["line"] is not None:
                rows.append((state["line"] - first, changes))
            if event == "line":
                state["steps"] += 1
                if state["steps"] > max_steps:
                    raise RuntimeError(f"more than {max_steps} steps: infinite loop?")
                state["line"] = frame.f_lineno
        return local

    def global_tracer(frame, event, arg):
        if event == "call" and frame.f_code is code:
            rows.append((0, diff(frame)))
            return local
        return None

    old = sys.gettrace()
    sys.settrace(global_tracer)
    try:
        result = func(*args)
    finally:
        sys.settrace(old)
    return rows, result


def render(func: Callable[..., Any], rows: list) -> list[str]:
    source, _ = inspect.getsourcelines(func)
    out = []
    for step, (line, changes) in enumerate(rows):
        text = "(call)" if line == 0 else source[line].strip()
        pairs = ", ".join(f"{k}={v}" for k, v in changes.items()) or "-"
        out.append(f"{step:>2}  L{line:<2} {text:<38} {pairs}")
    return out


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
