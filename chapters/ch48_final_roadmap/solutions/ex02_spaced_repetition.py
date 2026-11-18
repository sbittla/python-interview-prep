"""
Exercise 02 — Spaced-Repetition Scheduler from a Practice Log    [Tier: ★ Core]
Chapter 48 · Pattern: grouping + date arithmetic · Target time: 30 min

Problem
-------
You keep a practice log (``data/practice_log.csv``) with one row per attempt:
``date, problem, pattern, result, minutes`` where ``result`` is ``solved``, ``struggled`` or
``failed``. Using the revisit ladder from Chapter 3 (1, 3, 7, 21 days), compute when each problem
is next due:

* last result ``failed`` or ``struggled`` -> due 1 day after that attempt (the ladder restarts);
* last result ``solved`` -> look at the streak of consecutive ``solved`` results at the end of the
  history; streak 1 -> +1 day, 2 -> +3, 3 -> +7, 4 -> +21; a streak of 5 or more is *retired*.

Then, for a fixed "today", list overdue / due-today / upcoming reviews, an agenda for the next
7 days, and rank patterns by weakness (lowest clean-solve rate first, then slowest average).

Examples
--------
>>> next_review([("2026-11-02", "solved"), ("2026-11-09", "solved")])
('2026-11-12', 2)
>>> next_review([("2026-11-05", "failed")])
('2026-11-06', 0)

Constraints
-----------
- Dates are ISO ``YYYY-MM-DD``; the log may be unsorted; problems may appear many times.
- "today" is passed in (default ``2026-11-18``) so the output is deterministic.
- Unknown ``result`` values -> ``ValueError`` naming the row.

Hints
-----
- Group attempts by problem with ``defaultdict(list)`` and sort each group by date.
- Count the trailing streak by walking the attempts backwards.
- ``datetime.date.fromisoformat`` + ``timedelta(days=n)`` handle all the date maths.

Approach ladder
---------------
1. Brute force — for every day in the next month, rescan the whole log: O(D·N).
2. Improved   — group once, compute one due date per problem: O(N log N) for the sorts.
3. Optimal    — same grouping, plus a single pass to bucket by status and a ``Counter``-style
   pattern table; everything is O(N log N) and trivially testable because "today" is injected.

Follow-ups
----------
- Use minutes as a signal: a ``solved`` that took more than the target time counts as ``struggled``.
- Replace the fixed ladder with an SM-2 style ease factor.
- Weight the daily cap by how many minutes each review is likely to take.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "practice_log.csv"
LADDER = (1, 3, 7, 21)
RESULTS = ("solved", "struggled", "failed")
TODAY = "2026-11-18"


def load_log(path: Path = DATA) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for i, row in enumerate(rows, start=2):  # line 1 is the header
        if row["result"] not in RESULTS:
            raise ValueError(f"line {i}: unknown result {row['result']!r}")
        row["minutes"] = int(row["minutes"])
    return rows


def next_review(attempts: list[tuple[str, str]]) -> tuple[str | None, int]:
    """Return (due_date or None if retired, current solved streak)."""
    if not attempts:
        raise ValueError("no attempts")
    attempts = sorted(attempts)
    last_day = date.fromisoformat(attempts[-1][0])
    streak = 0
    for _, result in reversed(attempts):
        if result != "solved":
            break
        streak += 1
    if streak == 0:
        return (last_day + timedelta(days=LADDER[0])).isoformat(), 0
    if streak > len(LADDER):
        return None, streak
    return (last_day + timedelta(days=LADDER[streak - 1])).isoformat(), streak


def schedule(rows: list[dict], today: str = TODAY) -> list[dict]:
    by_problem: dict[str, list[tuple[str, str]]] = defaultdict(list)
    pattern_of: dict[str, str] = {}
    for r in rows:
        by_problem[r["problem"]].append((r["date"], r["result"]))
        pattern_of[r["problem"]] = r["pattern"]
    out = []
    for problem, attempts in by_problem.items():
        due, streak = next_review(attempts)
        last = max(attempts)[1]
        if due is None:
            status = "retired"
        elif due < today:
            status = "overdue"
        elif due == today:
            status = "due today"
        else:
            status = "upcoming"
        out.append({"problem": problem, "pattern": pattern_of[problem], "due": due,
                    "streak": streak, "last": last, "status": status,
                    "attempts": len(attempts)})
    out.sort(key=lambda d: (d["due"] or "9999-12-31", d["problem"]))
    return out


def agenda(items: list[dict], today: str = TODAY, days: int = 7,
           max_per_day: int = 3) -> dict[str, list[str]]:
    """Map each of the next ``days`` dates to at most ``max_per_day`` reviews.

    Overdue items roll forward into today; anything that does not fit is pushed to the next
    day, oldest due date first (ties: failed/struggled before solved, then by name).
    """
    start = date.fromisoformat(today)
    plan = {(start + timedelta(days=d)).isoformat(): [] for d in range(days)}
    queue = sorted((it for it in items if it["due"] is not None),
                   key=lambda it: (it["due"], it["streak"], it["problem"]))
    carry: list[str] = []
    for day in plan:
        carry += [it["problem"] for it in queue if max(it["due"], today) == day]
        plan[day], carry = carry[:max_per_day], carry[max_per_day:]
    return plan


def pattern_weakness(rows: list[dict]) -> list[tuple[str, int, float, float]]:
    """(pattern, attempts, clean-solve rate, average minutes), weakest first."""
    stats: dict[str, list] = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        s = stats[r["pattern"]]
        s[0] += 1
        s[1] += r["result"] == "solved"
        s[2] += r["minutes"]
    table = [(p, n, solved / n, mins / n) for p, (n, solved, mins) in stats.items()]
    table.sort(key=lambda t: (t[2], -t[3], t[0]))
    return table


def main() -> None:
    rows = load_log()
    print(f"Practice log: {len(rows)} attempts, {len({r['problem'] for r in rows})} problems, today = {TODAY}")
    print()
    print(f"{'problem':<28} {'pattern':<20} {'last':<10} {'streak':>6}  {'due':<10}  status")
    for it in schedule(rows):
        print(f"{it['problem']:<28} {it['pattern']:<20} {it['last']:<10} {it['streak']:>6}  "
              f"{it['due'] or '-':<10}  {it['status']}")
    print()
    print("Agenda, max 3 reviews per day (overdue first):")
    for day, probs in agenda(schedule(rows)).items():
        print(f"  {day}: {', '.join(probs) if probs else '(rest)'}")
    print()
    print("Weakest patterns first:")
    for p, n, rate, mins in pattern_weakness(rows)[:5]:
        print(f"  {p:<20} attempts={n} clean-solve={rate:.0%} avg={mins:.1f} min")
    print()
    print("Ladder demo for one problem solved again and again:")
    history = []
    for d in ["2026-11-01", "2026-11-02", "2026-11-05", "2026-11-12", "2026-12-03"]:
        history.append((d, "solved"))
        print(f"  after {d}: next = {next_review(history)}")


if __name__ == "__main__":
    main()
