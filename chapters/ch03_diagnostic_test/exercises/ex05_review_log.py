"""
Exercise 05 — Setting Up a Spaced-Repetition Log (1, 3, 7, 21 days) [Tier: ★ Core]
Chapter 03 · Pattern: append-only log + date arithmetic · Target time: 25 min

Problem
-------
Every question you miss on the diagnostic (and, later, every practice problem) goes into a
review log: a CSV with one row per attempt, header ``date,problem,pattern,result,minutes``
(``result`` is ``solved``, ``struggled`` or ``failed``). This is the same format Chapter 48's
scheduler reads (chapters/ch48_final_roadmap/solutions/ex02_spaced_repetition.py).

The revisit rule (the "ladder"):
- the last attempt was not ``solved`` -> due 1 day later (the ladder restarts);
- otherwise count the trailing run of ``solved`` attempts, the *streak*: streak 1 -> +1 day,
  2 -> +3, 3 -> +7, 4 -> +21; streak 5 or more -> retired (``None``).

Write:
1. ``next_due(last_day, streak)`` -> ISO date or None.
2. ``projected_dates(day, result)`` -> the review dates you will see if every later review is
   solved (the calendar you write into your notebook on day one).
3. ``seed_from_diagnostic(missed, day)`` -> log rows for missed question ids: pattern = the
   diagnostic area, result ``failed``, minutes 1 (Q1-28) or 15 (coding Q29-30).
4. ``record(rows, day, problem, pattern, result, minutes)`` -> append one validated row.
5. ``due(rows, today)`` -> sorted list of (due_date, problem) with due_date <= today
   (overdue first; retired problems never appear).
6. ``write_log(rows, path)`` / ``read_log(path)`` -> CSV round trip.

Examples
--------
>>> next_due("2026-11-18", 0)
'2026-11-19'
>>> projected_dates("2026-11-18", "failed")
['2026-11-19', '2026-11-20', '2026-11-23', '2026-11-30', '2026-12-21']

Constraints
-----------
- Dates are ISO ``YYYY-MM-DD`` and "today" is passed in, so output is deterministic.
- Unknown ``result`` -> ValueError; the log may be unsorted.
- Same-day tie-break: attempts are sorted per problem by date ONLY, with a stable sort, so
  several attempts on the same day keep their file order and the last row in the file is the
  latest attempt.

Hints
-----
- date.fromisoformat + timedelta(days=n) handles all date maths.
- Group rows by problem with defaultdict(list); sort each group by date (sort is stable).
- The streak is the run of 'solved' at the END of the history: walk it backwards.
- csv.DictReader returns strings: convert minutes back to int.

Follow-ups
----------
- Chapter 48 (ex02) builds the full scheduler on this log: daily caps, an agenda for the
  next 7 days and a weakest-pattern ranking.
- Treat a ``solved`` that took more than the target time as ``struggled``.
"""
from __future__ import annotations

import csv
import tempfile
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

LADDER = (1, 3, 7, 21)
RESULTS = ("solved", "struggled", "failed")
FIELDS = ["date", "problem", "pattern", "result", "minutes"]
AREA_RANGES = {"core": range(1, 9), "gotchas": range(9, 17),
               "complexity": range(17, 29), "coding": range(29, 31)}
TODAY = "2026-11-18"


def _shift(day: str, days: int) -> str:
    return (date.fromisoformat(day) + timedelta(days=days)).isoformat()


def next_due(last_day: str, streak: int) -> str | None:
    raise NotImplementedError("TODO")


def projected_dates(day: str, result: str) -> list[str]:
    raise NotImplementedError("TODO")


def seed_from_diagnostic(missed: list[int], day: str) -> list[dict]:
    raise NotImplementedError("TODO")


def record(rows: list[dict], day: str, problem: str, pattern: str,
           result: str, minutes: int) -> None:
    raise NotImplementedError("TODO")


def _streak(results: list[str]) -> int:
    raise NotImplementedError("TODO")


def due(rows: list[dict], today: str = TODAY) -> list[tuple[str, str]]:
    raise NotImplementedError("TODO")


def write_log(rows: list[dict], path: Path) -> None:
    raise NotImplementedError("TODO")


def read_log(path: Path) -> list[dict]:
    raise NotImplementedError("TODO")


def main() -> None:
    print("Projected reviews if every review is solved:")
    for result in ("failed", "solved"):
        print(f"  {result:<7} on {TODAY}: {projected_dates(TODAY, result)}")
    print()
    missed = [2, 9, 11, 13, 14, 19, 27, 28, 30]          # the sample sheet from ex01
    log = seed_from_diagnostic(missed, TODAY)
    print(f"Seeded {len(log)} rows; due on 2026-11-19: {len(due(log, '2026-11-19'))} items")
    pattern = {r["problem"]: r["pattern"] for r in log}
    for day, wrong in (("2026-11-19", {"diag-Q11", "diag-Q30"}), ("2026-11-20", set())):
        for _, problem in due(log, day):            # review everything that is due
            result = "failed" if problem in wrong else "solved"
            record(log, day, problem, pattern[problem], result, 1)
    print("Reviewed on 11-19 (Q11, Q30 still wrong) and 11-20 (all right). Next due:")
    upcoming: dict[str, list[str]] = defaultdict(list)
    for when, problem in due(log, "2099-12-31"):    # far future = every live item
        upcoming[when].append(problem)
    for when, problems in upcoming.items():
        print(f"  {when}: {problems}")
    print()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "practice_log.csv"
        write_log(log, path)
        back = read_log(path)
        lines = path.read_text(encoding="utf-8").splitlines()
    print(f"CSV round trip equal: {back == log}; {len(lines) - 1} rows. First lines:")
    for line in lines[:3]:
        print("  " + line)
    try:
        record(log, TODAY, "x", "core", "meh", 1)
    except ValueError as exc:
        print("Bad result ->", exc)


if __name__ == "__main__":
    main()
