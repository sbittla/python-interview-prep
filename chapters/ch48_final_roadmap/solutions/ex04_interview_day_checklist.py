"""
Exercise 04 — Interview-Day Checklist Printer                  [Tier: ★ Core]
Chapter 48 · Pattern: date arithmetic + largest-remainder rounding · Target time: 25 min

Problem
-------
Given the interview start (``YYYY-MM-DD HH:MM``), the format (``virtual`` or ``onsite``) and the
round length in minutes, print:

1. a countdown checklist with the *absolute* date/time of every step — T-14 days (weak-area
   repair starts), T-48 h, T-24 h, the morning of, T-30 min, T-5 min, and the after-interview
   steps (notes within 1 h, thank-you within 24 h);
2. a per-phase timing plan for the round. The reference split for a 60-minute round is
   intro 3, clarify 5, examples 4, brute force 4, optimise 6, code 23, test 10, questions 5.
   For other lengths scale proportionally and round with the **largest-remainder method** so the
   phases still sum exactly to the round length, and print the clock time each phase starts.

Examples
--------
>>> phase_plan(60)["code"]
23
>>> sum(phase_plan(45).values())
45

Constraints
-----------
- Round length 20–120 minutes, otherwise ``ValueError``.
- Format-specific items: virtual -> test camera/mic/editor, quiet room, charger;
  onsite -> route, ID, arrive 15 min early.
- Dates are fixed inputs, so the output is deterministic; weekday names come from a tuple
  (``strftime('%a')`` is locale-dependent).

Hints
-----
- ``datetime.fromisoformat("2026-12-03 10:00")`` parses the start; subtract ``timedelta``s.
- Largest remainder: floor every scaled value, then hand the missing minutes to the phases with
  the largest fractional parts (ties by original order).

Approach ladder
---------------
1. Brute force — hard-code one checklist string per format: dates must be edited by hand.
2. Improved   — compute dates from offsets; use ``round()`` for phases (sum can drift by ±1-2).
3. Optimal    — offsets as data + largest-remainder rounding: exact sums, O(P log P) for P phases.

Follow-ups
----------
- Multiple rounds in one day (onsite loop): chain the plans with breaks.
- Emit an ``.ics`` calendar file with reminders (write to a temporary directory).
"""
from __future__ import annotations

from datetime import datetime, timedelta

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
BASE_60 = {"intro": 3, "clarify": 5, "examples": 4, "brute force": 4, "optimise": 6,
           "code": 23, "test": 10, "questions": 5}

COMMON = [
    (timedelta(days=-14), "Start weak-area repair: top 3 areas from the readiness scorer"),
    (timedelta(days=-7), "Last full mock under real timing; score it with the rubric"),
    (timedelta(hours=-48), "Stop new topics. Revise summary cards, gotchas, complexity table"),
    (timedelta(hours=-24), "Light review only: 2 easy warm-ups, re-read the playbook; sleep early"),
    (timedelta(hours=-3), "Breakfast/water; one warm-up problem you have solved before"),
    (timedelta(minutes=-30), "Open blank editor, pen and paper; notifications off"),
    (timedelta(minutes=-5), "Breathe; first sentence ready: restate the problem"),
    (timedelta(hours=1, minutes=0), "Write notes: questions, what went well, what to fix"),
    (timedelta(hours=24), "Send a short thank-you; log problems into the practice log"),
]
FORMAT_ITEMS = {
    "virtual": [
        (timedelta(hours=-24), "Test camera, mic, screen share and the interview editor link"),
        (timedelta(minutes=-30), "Quiet room, charger plugged in, backup hotspot ready"),
    ],
    "onsite": [
        (timedelta(hours=-24), "Plan the route, pack ID, confirm the host's name and building"),
        (timedelta(minutes=-45), "Arrive 15 minutes early; find the reception"),
    ],
}


def _stamp(t: datetime) -> str:
    return f"{DAYS[t.weekday()]} {t:%Y-%m-%d %H:%M}"


def checklist(start: str, fmt: str) -> list[tuple[str, str, str]]:
    """Return (absolute time, relative label, item), chronologically."""
    if fmt not in FORMAT_ITEMS:
        raise ValueError(f"format must be one of {sorted(FORMAT_ITEMS)}")
    t0 = datetime.fromisoformat(start)
    items = COMMON + FORMAT_ITEMS[fmt]
    rows = []
    for offset, text in items:
        when = t0 + offset
        rows.append((when, relative(offset), text))
    rows.sort(key=lambda r: r[0])  # stable: common items keep their order on ties
    return [(_stamp(w), rel, text) for w, rel, text in rows]


def relative(offset: timedelta) -> str:
    sign = "-" if offset < timedelta(0) else "+"
    mins = abs(int(offset.total_seconds())) // 60
    if mins % (24 * 60) == 0 and mins >= 24 * 60 * 3:
        return f"T{sign}{mins // (24 * 60)}d"
    if mins % 60 == 0:
        return f"T{sign}{mins // 60}h"
    return f"T{sign}{mins}m"


def phase_plan(minutes: int) -> dict[str, int]:
    if not 20 <= minutes <= 120:
        raise ValueError("round length must be 20-120 minutes")
    scaled = [(name, v * minutes / 60) for name, v in BASE_60.items()]
    floors = {name: int(x) for name, x in scaled}
    missing = minutes - sum(floors.values())
    order = sorted(range(len(scaled)), key=lambda i: (-(scaled[i][1] - int(scaled[i][1])), i))
    for i in order[:missing]:
        floors[scaled[i][0]] += 1
    return floors


def phase_schedule(start: str, minutes: int) -> list[tuple[str, str, int]]:
    t = datetime.fromisoformat(start)
    out = []
    for name, m in phase_plan(minutes).items():
        out.append((f"{t:%H:%M}", name, m))
        t += timedelta(minutes=m)
    return out


def main() -> None:
    start, fmt, length = "2026-12-03 10:00", "virtual", 60
    print(f"Interview: {_stamp(datetime.fromisoformat(start))} | {fmt} | {length}-minute coding round")
    print()
    for when, rel, text in checklist(start, fmt):
        print(f"[ ] {when}  {rel:>6}  {text}")
    print()
    print("Phase plan:")
    for clock, name, m in phase_schedule(start, length):
        print(f"  {clock}  {name:<12} {m:>2} min")
    print()
    for n in (45, 90):
        plan = phase_plan(n)
        print(f"{n}-minute round: " + ", ".join(f"{k} {v}" for k, v in plan.items())
              + f"  (sum {sum(plan.values())})")
    print()
    print("Onsite differences:")
    for when, rel, text in checklist("2026-12-10 13:30", "onsite"):
        if text in {t for _, t in FORMAT_ITEMS["onsite"]}:
            print(f"[ ] {when}  {rel:>6}  {text}")
    for bad in (10, 150):
        try:
            phase_plan(bad)
        except ValueError as exc:
            print(f"phase_plan({bad}) -> ValueError: {exc}")


if __name__ == "__main__":
    main()
