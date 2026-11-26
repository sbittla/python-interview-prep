"""
Exercise 04 — Progress Tracker: Trends, Weakest Criteria, Study Plan   [Tier: ◆ Extended]
Chapter 47 · Pattern: group by rubric + least squares + ranked deficits · Target time: 30 min

Problem
-------
``data/scores.csv`` has one row per mock: date, mock id, rubric ("coding" or "ai") and
ratings as "key=rating;key=rating;...". Score each row with Exercise 01's ``score``
(so all validation is reused), then for ONE rubric at a time:

1. ``history(entries, rubric)`` -> [(date, mock, total, verdict)] in date order.
2. ``trend(totals)`` -> least-squares slope of total against mock number (0, 1, 2, ...),
   as an exact Fraction; 0 for fewer than two mocks.
3. ``weakest(entries, rubric, n=2, window=3)`` -> the n criteria with the largest MEAN
   POINTS LOST over the last ``window`` mocks of that rubric (points, not raw ratings:
   a weak 25-point criterion matters more than a weak 10-point one). Ties: rubric order.
   Returns [(key, mean_lost)].
4. ``study_plan(entries, rubric)`` -> one line per weakest criterion: its next step
   (Exercise 01's ``NEXT_STEP``) and the mock to retake, i.e. the mock in the window
   with the lowest rating on that criterion (ties: the most recent).

Examples
--------
>>> trend([50, 60, 70])
Fraction(10, 1)

Constraints
-----------
- Dates are ISO strings, so string order is date order.
- An empty history for a rubric raises ValueError.

Hints
-----
- Reuse Exercise 01's ``score`` for every row: it already validates the ratings
  (so finish Exercise 01 first; this file imports it).
- slope = sum((x - x_mean) * (y - y_mean)) / sum((x - x_mean) ** 2), x = 0..n-1, in Fraction.
- Row i of every Scorecard is the same criterion, so average ``rows[i].lost`` over the window.
- Retake: ``min`` over ``enumerate(recent)`` keyed by (rating, -position).
- Study-plan line: f"{key} (avg -{float(lost):.2f} pts): {NEXT_STEP[key]}; retake {mock}".

Follow-ups
----------
- Flag a plateau: slope near 0 over the last four mocks.
- Report each criterion's own slope to show which habit is improving.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from ex01_rubric_scorer import AI_RUBRIC, CODING_RUBRIC, NEXT_STEP, Scorecard, score

DATA = Path(__file__).resolve().parent.parent / "data" / "scores.csv"
RUBRICS = {"coding": CODING_RUBRIC, "ai": AI_RUBRIC}


@dataclass(frozen=True)
class Entry:
    date: str
    mock: str
    rubric: str
    card: Scorecard


def parse_ratings(text: str) -> dict[str, int]:
    out = {}
    for part in text.split(";"):
        key, _, value = part.partition("=")
        if not value.strip().lstrip("-").isdigit():
            raise ValueError(f"bad rating {part!r}")
        if key.strip() in out:
            raise ValueError(f"duplicate key {key.strip()!r}")
        out[key.strip()] = int(value)
    return out


def load_scores(path: Path = DATA) -> list[Entry]:
    raise NotImplementedError("TODO")


def _select(entries: list[Entry], rubric: str) -> list[Entry]:
    chosen = sorted((e for e in entries if e.rubric == rubric), key=lambda e: e.date)
    if not chosen:
        raise ValueError(f"no mocks scored with rubric {rubric!r}")
    return chosen


def history(entries, rubric):
    raise NotImplementedError("TODO")


def trend(totals) -> Fraction:
    raise NotImplementedError("TODO")


def weakest(entries, rubric, n=2, window=3):
    raise NotImplementedError("TODO")


def study_plan(entries, rubric, n=2, window=3):
    raise NotImplementedError("TODO")


def main() -> None:
    entries = load_scores()
    for rubric in ("coding", "ai"):
        rows = history(entries, rubric)
        print(f"{rubric} rubric, {len(rows)} mocks:")
        for date, mock, total, verdict in rows:
            print(f"  {date} {mock} {float(total):6.2f}  {verdict}")
        slope = trend([t for _, _, t, _ in rows])
        print(f"  trend: {float(slope):+.2f} points per mock")
        for key, lost in weakest(entries, rubric):
            print(f"  weak: {key:<13} avg lost {float(lost):.2f} (last {min(3, len(rows))})")
    print("\nStudy plan (coding):")
    for line in study_plan(entries, "coding"):
        print(" ", line)


if __name__ == "__main__":
    main()
