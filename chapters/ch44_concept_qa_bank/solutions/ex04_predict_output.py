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

Approach ladder
---------------
1. Hand-written answers — O(1) to write, silently wrong after any edit.
2. Run each snippet in a subprocess — exact isolation, but ~tens of ms of
   interpreter start-up per snippet.
3. ``exec`` with ``contextlib.redirect_stdout`` in a fresh dict — O(snippet)
   with no start-up cost; isolation is per-namespace, which is enough for
   short, trusted snippets. Move up from rung 1 because tests now fail the
   moment the key and reality disagree.

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
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            exec(compile(code, "<snippet>", "exec"), {"__name__": "__snippet__"})
        except Exception as exc:              # report the type only; messages vary
            print(f"raises {type(exc).__name__}")
    return buf.getvalue()


def check(items: list[dict]) -> list[tuple[str, str, str]]:
    bad = []
    for it in items:
        actual = run_snippet(it["code"])
        if actual != it["expected"]:
            bad.append((it["id"], it["expected"], actual))
    return bad


def quiz_sheet(items: list[dict], set_name: str) -> str:
    parts = []
    for it in items:
        if it["set"] == set_name:
            parts.append(f"[{it['id']}] {it['xref']}\n{it['code']}\n")
    return "\n".join(parts)


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
