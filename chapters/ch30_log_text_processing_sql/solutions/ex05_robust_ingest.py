"""
Exercise 05 — Ingest Malformed JSON Lines Without Crashing or Lying   [Tier: ★ Core]
Chapter 30 · Pattern: narrow except + explicit validation + error budget · Target time: 25 min

Problem
-------
`data/payments.jsonl` holds one JSON object per line: {"user": str, "amount": int >= 0,
"ts": int}; extra keys are allowed. Some lines are broken. Write

1. `validate(obj)` -> None if `obj` is a valid payment, else a short reason string;
2. `ingest(raw_lines, max_bad_ratio)` over an iterable of BYTES lines ->
   (good: list[dict], bad: list[(line_no, reason)]). Blank lines are skipped silently.
   If more than `max_bad_ratio` of the non-blank lines are bad, raise `TooManyErrors`
   (the input is probably the wrong file, and quietly keeping 10 % of it would lie).

Reasons: "bad utf-8", "bad json", "not an object", "missing <field>",
"<field> must be <type>", "amount < 0".

Examples
--------
>>> validate({"user": "a", "amount": 3, "ts": 1})
>>> validate({"user": "a", "amount": True, "ts": 1})
'amount must be int'
>>> ingest([b'{"user": "a", "amount": 1, "ts": 2}', b'{oops'], 0.5)
([{'user': 'a', 'amount': 1, 'ts': 2}], [(2, 'bad json')])

Constraints
-----------
- One pass, O(total bytes) time; memory O(good records) (or O(1) if you yield instead).

Approach ladder
---------------
1. `json.loads(line)` with no handling — the first bad line crashes the whole job.
2. `try: ... except Exception: continue` — never crashes, but also swallows your own
   bugs (a KeyError in your code looks like "bad data") and reports nothing.
3. Decode strictly, catch only `UnicodeDecodeError` / `json.JSONDecodeError`, validate
   fields explicitly, record (line_no, reason), and enforce an error budget.
   Why move up: rung 3 is the only one that both survives bad input and tells you about it.

Hints
-----
- `isinstance(True, int)` is True (bool subclasses int); reject bools explicitly.
- `enumerate(lines, 1)` gives human line numbers.
- `json.JSONDecodeError` is a subclass of `ValueError`.

Edge cases
----------
- Truncated JSON, valid JSON that is a list, missing field, wrong type ("80"), bool as
  int, negative amount, invalid UTF-8 byte, trailing spaces, blank line, extra keys,
  all lines bad (budget trips), empty input (no division by zero).

Follow-ups
----------
- Write bad lines to a quarantine file ("dead-letter queue") for replay after a fix.
- Lenient decoding: `raw.decode("utf-8", errors="replace")` keeps the line but inserts
  U+FFFD; decide per field whether that is acceptable.
- Schema evolution: version field, defaults for new optional keys.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

DATA = Path(__file__).resolve().parent.parent / "data"
SCHEMA = {"user": str, "amount": int, "ts": int}


class TooManyErrors(ValueError):
    pass


def validate(obj: Any) -> str | None:
    if not isinstance(obj, dict):
        return "not an object"
    for field, typ in SCHEMA.items():
        if field not in obj:
            return f"missing {field}"
        value = obj[field]
        if isinstance(value, bool) or not isinstance(value, typ):
            return f"{field} must be {typ.__name__}"
    if obj["amount"] < 0:
        return "amount < 0"
    return None


def ingest(raw_lines: Iterable[bytes], max_bad_ratio: float = 0.5
           ) -> tuple[list[dict], list[tuple[int, str]]]:
    good: list[dict] = []
    bad: list[tuple[int, str]] = []
    for n, raw in enumerate(raw_lines, 1):
        try:
            line = raw.decode("utf-8").strip()
        except UnicodeDecodeError:
            bad.append((n, "bad utf-8"))
            continue
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            bad.append((n, "bad json"))
            continue
        reason = validate(obj)
        if reason:
            bad.append((n, reason))
        else:
            good.append(obj)
    seen = len(good) + len(bad)
    if seen and len(bad) / seen > max_bad_ratio:
        raise TooManyErrors(f"{len(bad)}/{seen} lines bad")
    return good, bad


def naive_ingest(raw_lines: Iterable[bytes]) -> list[dict]:
    """Rung 1: crashes on the first bad line."""
    return [json.loads(raw) for raw in raw_lines if raw.strip()]


def main() -> None:
    with open(DATA / "payments.jsonl", "rb") as f:          # bytes: we decode per line
        raw = list(f)
    try:
        naive_ingest(raw)
    except ValueError as e:                                  # JSONDecodeError or UnicodeDecodeError
        print("naive:", type(e).__name__)
    good, bad = ingest(raw, max_bad_ratio=0.5)
    print("good users:", [g["user"] for g in good])
    print("total amount:", sum(g["amount"] for g in good))
    for n, reason in bad:
        print(f"  line {n}: {reason}")
    try:
        ingest(raw, max_bad_ratio=0.25)
    except TooManyErrors as e:
        print("budget 25%:", e)
    print("lenient decode:", ascii(raw[9].decode("utf-8", errors="replace")[:16]))
    print("empty:", ingest([]), "| blank only:", ingest([b"\n", b"  \n"]))


if __name__ == "__main__":
    main()
