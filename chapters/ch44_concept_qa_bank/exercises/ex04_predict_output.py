"""
Exercise 04 — "Predict the Output" Sets, Verified by Execution  [Tier: ★ Core]
Chapter 44 · Pattern: executable answer key · Target time: 20 min

Problem
-------
``data/predict_output.json`` holds short snippets grouped into sets
(references, scope, numbers, iteration, collections, equality):

    {"id": "po01", "set": "references", "xref": "§7.1",
     "code": "def add(x, bucket=[]): ...", "expected": "[1, 2] [1, 2]\\n"}

A written answer key drifts: someone edits a snippet and forgets the answer,
or a Python release changes behaviour. Make the key executable.

- ``run_snippet(code)`` — execute ``code`` in a fresh namespace
  (``{"__name__": "__snippet__"}``) and return everything it printed. If it
  raises an ``Exception``, append the line ``raises <ExceptionType>`` (type
  name only: messages differ between versions) and stop. ``sys.stdout``
  must be restored even then.
- ``check(items)`` — run every snippet and return ``(id, expected, actual)``
  for each mismatch, in input order.
- ``quiz_sheet(items, set_name)`` — the learner's sheet for one set: for each
  item a header ``[po01] §7.1`` and its code, but never the expected output.

Examples
--------
>>> run_snippet("print(-7 // 2)")
'-4\\n'
>>> run_snippet("[][0]")
'raises IndexError\\n'

Constraints
-----------
- Snippets must be deterministic: no ``id()``, timing, set order of strings
  or hash-dependent output.
- Trusted input only: ``exec`` runs arbitrary code, so never point this at a
  bank you did not write.

Hints
-----
- ``contextlib.redirect_stdout(io.StringIO())`` captures ``print`` output and
  restores ``sys.stdout`` when the ``with`` block exits, even on errors.
- Put the ``try``/``except Exception`` *inside* the ``with`` so the
  "raises ..." line is captured too.
- A fresh dict per call isolates snippets from each other.

Follow-ups
----------
- Capture warnings too (``warnings.catch_warnings(record=True)``) for
  snippets such as ``x is 257`` that emit ``SyntaxWarning``.
- Run the set under several Python versions in CI.
- Wrong-but-tempting: catching ``BaseException`` — that would also swallow
  ``KeyboardInterrupt`` and ``SystemExit``.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "predict_output.json"


def run_snippet(code: str) -> str:
    raise NotImplementedError("TODO")


def check(items: list[dict]) -> list[tuple[str, str, str]]:
    raise NotImplementedError("TODO")


def quiz_sheet(items: list[dict], set_name: str) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    items = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    sets: dict[str, int] = {}
    for it in items:
        sets[it["set"]] = sets.get(it["set"], 0) + 1
    print(f"{len(items)} snippets in {len(sets)} sets:", sets)
    print("mismatches:", check(items))
    print()
    print("quiz sheet, set 'numbers':")
    print(quiz_sheet(items, "numbers"))
    print("answers:")
    for it in items:
        if it["set"] == "numbers":
            print(f"  [{it['id']}] {run_snippet(it['code']).rstrip()}")
    drifted = dict(items[0], expected="[1] [2]\n")    # a stale answer key
    print("stale key detected:", check([drifted]))


if __name__ == "__main__":
    main()
