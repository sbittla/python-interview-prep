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

Hints
-----
- Split the work into layers you can test alone: parse_row (one row ->
  Transaction or ValueError), parse_rows (loop + collect "line N: ..."
  errors), summarize (defaultdict(Decimal)), render_*, and a thin cli().
- csv.reader handles quoted commas; reader.line_num gives the physical line.
- Check the date's shape with re.fullmatch before date.fromisoformat: on 3.11+
  fromisoformat also accepts "20240301".
- Decimal(raw) raises decimal.InvalidOperation, not ValueError; also reject
  non-finite values such as "NaN".
- argparse prints usage to sys.stderr and raises SystemExit: wrap parse_args in
  contextlib.redirect_stdout(out) / redirect_stderr(err) and return the code.
- Catch FileNotFoundError, UnicodeDecodeError and OSError when reading: exit 1.

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
    raise NotImplementedError("TODO")


def parse_rows(lines: Iterable[str]) -> tuple[list[Transaction], list[str]]:
    """Parse CSV lines (header first); collect per-row errors instead of crashing."""
    raise NotImplementedError("TODO")


# --- compute -----------------------------------------------------------------
def summarize(txns: Iterable[Transaction], month: str | None = None) -> list[tuple[str, Decimal]]:
    """Total per category, largest first; ties broken by category name."""
    raise NotImplementedError("TODO")


# --- render ------------------------------------------------------------------
def render_text(summary: list[tuple[str, Decimal]]) -> str:
    raise NotImplementedError("TODO")


def render_json(summary: list[tuple[str, Decimal]]) -> str:
    raise NotImplementedError("TODO")


# --- CLI ---------------------------------------------------------------------
def month_arg(value: str) -> str:
    raise NotImplementedError("TODO")


def build_parser() -> argparse.ArgumentParser:
    raise NotImplementedError("TODO")


def cli(argv: list[str], out: TextIO | None = None, err: TextIO | None = None) -> int:
    raise NotImplementedError("TODO")


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
