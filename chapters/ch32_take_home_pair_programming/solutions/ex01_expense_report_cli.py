"""
Exercise 01 — Sample Take-Home: Expense Summary CLI               [Tier: ★ Core]
Chapter 32 · Pattern: take-home structure (parse → validate → compute → render → CLI)
Target time: 90 min (a real take-home would allow 2–4 h)

Problem
-------
The brief: "Write a command-line tool that reads a CSV of personal transactions
(columns: date, category, amount, note) and prints the total spent per category,
largest first. Support an optional month filter and a JSON output mode. Treat
the data as messy." Build it as you would submit it:

- parse_rows(lines) -> (transactions, errors). Each bad row becomes an error
  string "line N: <reason>" (N = physical line where the record ends; header is line 1) instead of a
  crash. Reasons: "bad date '...'", "bad amount '...'", "missing category",
  "missing column(s)" (short row), and "unknown header ..." if the
  header is wrong (then no rows are parsed).
- summarize(transactions, month=None) -> [(category, total)] sorted by total
  descending, then category ascending. month is "YYYY-MM" or None (all).
- render_text(summary) / render_json(summary): aligned table / JSON
  {"category": "12.34", ...} preserving the summary's order.
- cli(argv, out, err) -> exit code. Usage:
  expense_report PATH [--month YYYY-MM] [--format text|json] [--strict].
  0 = success (row errors go to err as warnings), 1 = file missing, unreadable
  or not UTF-8, or --strict with row errors, 2 = bad arguments (argparse's
  convention). All text, including argparse's usage message, goes to out/err
  (default: sys.stdout/sys.stderr); no traceback ever reaches the user.
- Dates must be YYYY-MM-DD exactly: on Python 3.11+ date.fromisoformat also
  accepts "20240301" and "2024-W10-1", so check the shape first (3.10 portable).

Assumptions (state them in the README, do not silently guess)
---------------------------------------------------------------
- Amounts are decimal strings in one currency; negatives are refunds and are kept.
- Categories are case- and whitespace-insensitive: " Transport" == "transport".
- Money uses decimal.Decimal, never float: 0.1 + 0.2 must be 0.3.

Examples
--------
>>> txns, errs = parse_rows(["date,category,amount,note", "2024-03-01,food,1.10,", "x,food,1,"])
>>> [str(t.amount) for t in txns], errs
(['1.10'], ["line 3: bad date 'x'"])
>>> summarize(txns)
[('food', Decimal('1.10'))]

Constraints
-----------
- Standard library only; files are small enough to fit in memory.
- Pure core (no I/O in parse/summarize/render) so it is testable without files.

Approach ladder
---------------
1. Brute force — one 60-line main() that opens the file, splits on commas and
   sums floats. Works on the happy path; untestable, breaks on quoted commas,
   0.1 + 0.2 drift, one bad row kills the run.
2. Improved   — csv module + Decimal + a try/except per row; still one function,
   so tests need real files and capture stdout.
3. Optimal    — layers: a frozen dataclass model, pure parse/summarize/render
   functions, and a thin cli() that takes argv and output streams. Every layer
   is unit-tested directly; the CLI gets two end-to-end tests. O(n) time,
   O(c) space for c categories.

Follow-ups
----------
- Multiple currencies: add a currency column and a rate table; reject unknown
  codes rather than guessing.
- Files larger than memory: parse_rows already streams; summarize keeps only
  one running total per category.
- Package it: src/expense_report/{model,parse,report,cli}.py, a pyproject.toml
  console-script entry point, tests/ mirroring the modules.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import io
import json
import re
import sys
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TextIO

HEADER = ["date", "category", "amount", "note"]
DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")   # 3.11+ fromisoformat is looser
MONTH_RE = re.compile(r"[0-9]{4}-[0-9]{2}")
DATA = Path(__file__).resolve().parent.parent / "data" / "transactions.csv"


# --- model -----------------------------------------------------------------
@dataclass(frozen=True)
class Transaction:
    day: date
    category: str
    amount: Decimal
    note: str = ""


# --- parse + validate --------------------------------------------------------
def parse_row(row: list[str]) -> Transaction:
    """One CSV row -> Transaction; raises ValueError with a readable reason."""
    if len(row) < 3:
        raise ValueError("missing column(s)")
    raw_date, raw_cat, raw_amount = (cell.strip() for cell in row[:3])
    try:
        if not DATE_RE.fullmatch(raw_date):
            raise ValueError
        day = date.fromisoformat(raw_date)
    except ValueError:
        raise ValueError(f"bad date {raw_date!r}") from None
    try:
        amount = Decimal(raw_amount)
    except InvalidOperation:
        raise ValueError(f"bad amount {raw_amount!r}") from None
    if not amount.is_finite():
        raise ValueError(f"bad amount {raw_amount!r}")
    if not raw_cat:
        raise ValueError("missing category")
    note = row[3].strip() if len(row) > 3 else ""
    return Transaction(day, raw_cat.lower(), amount, note)


def parse_rows(lines: Iterable[str]) -> tuple[list[Transaction], list[str]]:
    """Parse CSV lines (header first); collect per-row errors instead of crashing."""
    reader = csv.reader(lines)
    header = next(reader, None)
    if header is None:
        return [], ["line 1: empty file"]
    if [h.strip().lower() for h in header] != HEADER:
        return [], [f"line 1: unknown header {header!r}, expected {HEADER!r}"]
    txns: list[Transaction] = []
    errors: list[str] = []
    for row in reader:
        line_no = reader.line_num                     # physical line, even with quoted newlines
        if not any(cell.strip() for cell in row):
            continue                                  # tolerate blank lines
        try:
            txns.append(parse_row(row))
        except ValueError as exc:
            errors.append(f"line {line_no}: {exc}")
    return txns, errors


# --- compute -----------------------------------------------------------------
def summarize(txns: Iterable[Transaction], month: str | None = None) -> list[tuple[str, Decimal]]:
    """Total per category, largest first; ties broken by category name."""
    totals: dict[str, Decimal] = defaultdict(Decimal)
    for t in txns:
        if month is None or t.day.isoformat()[:7] == month:
            totals[t.category] += t.amount
    return sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))


# --- render ------------------------------------------------------------------
def render_text(summary: list[tuple[str, Decimal]]) -> str:
    if not summary:
        return "no transactions\n"
    width = max(len("TOTAL"), *(len(cat) for cat, _ in summary))
    lines = [f"{cat:<{width}}  {total:>10.2f}" for cat, total in summary]
    grand = sum((total for _, total in summary), Decimal("0"))
    lines.append(f"{'TOTAL':<{width}}  {grand:>10.2f}")
    return "\n".join(lines) + "\n"


def render_json(summary: list[tuple[str, Decimal]]) -> str:
    return json.dumps({cat: f"{total:.2f}" for cat, total in summary}, indent=2) + "\n"


# --- CLI ---------------------------------------------------------------------
def month_arg(value: str) -> str:
    try:
        if not MONTH_RE.fullmatch(value):
            raise ValueError
        date.fromisoformat(value + "-01")
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM, got {value!r}") from None
    return value


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="expense_report", description="Totals per category.")
    p.add_argument("path", type=Path)
    p.add_argument("--month", type=month_arg, default=None)
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--strict", action="store_true", help="exit 1 if any row is invalid")
    return p


def cli(argv: list[str], out: TextIO | None = None, err: TextIO | None = None) -> int:
    out = sys.stdout if out is None else out      # resolved at call time, not import time
    err = sys.stderr if err is None else err
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            args = build_parser().parse_args(argv)  # usage/--help text goes to our streams
    except SystemExit as exc:                     # argparse exits on bad usage or --help
        return int(exc.code or 0)
    name = args.path.name
    try:
        with args.path.open(encoding="utf-8", newline="") as fh:
            txns, errors = parse_rows(fh)
    except FileNotFoundError:
        print(f"error: no such file: {name}", file=err)
        return 1
    except UnicodeDecodeError:
        print(f"error: {name} is not UTF-8 text", file=err)
        return 1
    except OSError as exc:                        # a directory, no permission, ...
        print(f"error: cannot read {name}: {exc.strerror}", file=err)
        return 1
    for e in errors:
        print(f"warning: {e}", file=err)
    if errors and args.strict:
        return 1
    summary = summarize(txns, args.month)
    out.write(render_json(summary) if args.format == "json" else render_text(summary))
    return 0


def run_demo(argv: list[str]) -> None:
    out, err = io.StringIO(), io.StringIO()
    code = cli(argv, out, err)
    shown = [a if not a.endswith(".csv") else Path(a).name for a in argv]
    print(f"$ expense_report {' '.join(shown)}   -> exit {code}")
    print(out.getvalue(), end="")
    for line in err.getvalue().splitlines():
        print(f"  [stderr] {line}")
    print()


def main() -> None:
    print("Decimal vs float: 0.1+0.2 ->", Decimal("0.1") + Decimal("0.2"), "vs", 0.1 + 0.2)
    print()
    path = str(DATA)
    run_demo([path, "--month", "2024-03"])
    run_demo([path, "--month", "2024-02", "--format", "json"])
    run_demo([path, "--strict"])
    run_demo([str(DATA.with_name("missing.csv"))])
    run_demo([path, "--month", "2024-3"])
    txns, errors = parse_rows(["date,category,amount,note"])
    print("header only:", txns, errors, "->", render_text(summarize(txns)), end="")
    print("wrong header:", parse_rows(["when,what,how much"])[1])


if __name__ == "__main__":
    main()
