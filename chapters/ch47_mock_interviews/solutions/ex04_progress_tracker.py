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

Approach ladder
---------------
1. Brute force — eyeball the latest score: one bad day looks like a trend.
2. Improved   — compare first and last totals: ignores everything in between.
3. Optimal    — least-squares slope over all mocks, weakness from a recent window,
   weighted by points. O(M·C) for M mocks and C criteria.

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
    entries = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rubric = RUBRICS.get(row["rubric"])
            if rubric is None:
                raise ValueError(f"unknown rubric {row['rubric']!r}")
            card = score(rubric, parse_ratings(row["ratings"]))
            entries.append(Entry(row["date"], row["mock"], row["rubric"], card))
    return entries


def _select(entries: list[Entry], rubric: str) -> list[Entry]:
    chosen = sorted((e for e in entries if e.rubric == rubric), key=lambda e: e.date)
    if not chosen:
        raise ValueError(f"no mocks scored with rubric {rubric!r}")
    return chosen


def history(entries, rubric):
    return [(e.date, e.mock, e.card.total, e.card.verdict) for e in _select(entries, rubric)]


def trend(totals) -> Fraction:
    n = len(totals)
    if n < 2:
        return Fraction(0)
    ys = [Fraction(y) for y in totals]
    x_mean, y_mean = Fraction(n - 1, 2), sum(ys) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in enumerate(ys))
    den = sum((x - x_mean) ** 2 for x in range(n))
    return num / den


def weakest(entries, rubric, n=2, window=3):
    recent = _select(entries, rubric)[-window:]
    keys = [k for k, _, _ in RUBRICS[rubric]]
    means = []
    for i, key in enumerate(keys):
        lost = sum(e.card.rows[i].lost for e in recent) / len(recent)
        means.append((key, lost, i))
    means.sort(key=lambda t: (-t[1], t[2]))
    return [(k, lost) for k, lost, _ in means[:n]]


def study_plan(entries, rubric, n=2, window=3):
    recent = _select(entries, rubric)[-window:]
    keys = [k for k, _, _ in RUBRICS[rubric]]
    lines = []
    for key, lost in weakest(entries, rubric, n, window):
        i = keys.index(key)
        # lowest rating; among ties the most recent (later index wins via -position)
        pos, worst = min(enumerate(recent), key=lambda pe: (pe[1].card.rows[i].rating, -pe[0]))
        lines.append(f"{key} (avg -{float(lost):.2f} pts): {NEXT_STEP[key]}; "
                     f"retake {worst.mock}")
    return lines


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
