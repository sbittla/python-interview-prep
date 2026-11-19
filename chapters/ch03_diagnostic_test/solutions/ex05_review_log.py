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

Approach ladder
---------------
1. Brute force — a paper calendar: write each review date by hand; nothing tells you what
   is overdue after a missed day.
2. Optimal    — store attempts, not due dates. Due dates are *derived* from the history, so a
   failed review automatically restarts the ladder and nothing goes stale. O(N log N) to
   group and sort N rows.

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
    if streak < 0:
        raise ValueError("streak must be >= 0")
    if streak == 0:
        return _shift(last_day, LADDER[0])
    if streak > len(LADDER):
        return None
    return _shift(last_day, LADDER[streak - 1])


def projected_dates(day: str, result: str) -> list[str]:
    if result not in RESULTS:
        raise ValueError(f"unknown result {result!r}")
    streak = 1 if result == "solved" else 0
    dates = []
    current = next_due(day, streak)
    while current is not None:
        dates.append(current)
        streak += 1                     # assume each review is solved
        current = next_due(current, streak)
    return dates


def seed_from_diagnostic(missed: list[int], day: str) -> list[dict]:
    rows = []
    for qid in sorted(missed):
        area = next((a for a, ids in AREA_RANGES.items() if qid in ids), None)
        if area is None:
            raise ValueError(f"no diagnostic question {qid}")
        rows.append({"date": day, "problem": f"diag-Q{qid:02d}", "pattern": area,
                     "result": "failed", "minutes": 15 if area == "coding" else 1})
    return rows


def record(rows: list[dict], day: str, problem: str, pattern: str,
           result: str, minutes: int) -> None:
    if result not in RESULTS:
        raise ValueError(f"unknown result {result!r}")
    date.fromisoformat(day)             # raises ValueError on a malformed date
    rows.append({"date": day, "problem": problem, "pattern": pattern,
                 "result": result, "minutes": int(minutes)})


def _streak(results: list[str]) -> int:
    streak = 0
    for r in reversed(results):
        if r != "solved":
            break
        streak += 1
    return streak


def due(rows: list[dict], today: str = TODAY) -> list[tuple[str, str]]:
    history: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["result"] not in RESULTS:
            raise ValueError(f"unknown result {row['result']!r} for {row['problem']}")
        history[row["problem"]].append(row)
    out = []
    for problem, attempts in history.items():
        attempts.sort(key=lambda r: r["date"])         # stable: file order on equal dates
        when = next_due(attempts[-1]["date"], _streak([r["result"] for r in attempts]))
        if when is not None and when <= today:
            out.append((when, problem))
    return sorted(out)


def write_log(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def read_log(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        row["minutes"] = int(row["minutes"])
    return rows


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
