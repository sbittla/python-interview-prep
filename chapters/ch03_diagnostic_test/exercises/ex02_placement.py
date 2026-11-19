"""
Exercise 02 — Placement: Scores -> Path -> Weekly Plan             [Tier: ★ Core]
Chapter 03 · Pattern: decision table + templating · Target time: 25 min

Problem
-------
Turn the area scores produced by ex01's ``grade`` into a study decision.

1. ``percentages(scores)`` -> {area: fraction 0.0-1.0} using MAX_POINTS
   (core 8, gotchas 8, complexity 12, coding 8; total 36).
2. ``place(scores)`` -> {"path", "overall", "weak"}:
   - overall < 40 %                         -> "foundations"
   - every area >= 75 % (PASS)              -> "fast"   (skim Part I, start at Part II)
   - otherwise                              -> "full"
   "weak" lists the areas below 75 %, weakest first (ties in AREA order).
3. ``choose_plan(path, weeks_available)`` -> (plan_name, warning). Refines Chapter 1's
   time-only rule (ch01 ex06) with the diagnostic's evidence:
   - fast:        < 8 weeks -> "crash-4";        otherwise "standard-8"
   - full:        < 8 weeks -> "crash-4" + warning; otherwise "standard-8"
   - foundations: >= 12 weeks -> "foundations-12"; otherwise "standard-8" + warning
4. ``weekly_plan(scores, track, weeks_available)`` -> {"path", "plan", "warning", "weeks"}
   where weeks is a list of (week_number, focus). Track weeks come from TRACK_WEEKS
   (the S/M/L tracks of Chapter 1). Week 1 gets "Repair: ..." for each weak area and ends
   with a diagnostic retake; on the fast path, Part I is skimmed rather than studied. In
   "foundations-12" the four foundation weeks are the repair, so the retake moves to week 4.

Examples
--------
>>> place({"core": 8, "gotchas": 7, "complexity": 11, "coding": 8})["path"]
'fast'
>>> choose_plan("full", 5)
('crash-4', True)

Constraints
-----------
- track in {"S", "M", "L"} and weeks_available >= 1, else ValueError.
- Area scores must lie in 0..MAX_POINTS[area], else ValueError.

Hints
-----
- Compute fractions first; every rule then reads like the table in the docstring.
- sorted(..., key=pct) is stable, so ties keep AREA order.
- Build the standard plan once, then substitute the TRACK-1/TRACK-2 placeholders.
- Replace "role track" with "track S/M/L" in the crash plan. Copy table lists before editing them so the module-level tables never change.

Follow-ups
----------
- Make the 75 % threshold per area (e.g. coding 50 %) and test the boundary values.
- Weight the plan by hours per week, not only by the number of weeks.
"""
from __future__ import annotations

AREAS = ("core", "gotchas", "complexity", "coding")
MAX_POINTS = {"core": 8, "gotchas": 8, "complexity": 12, "coding": 8}
PASS = 0.75
FOUNDATIONS_BELOW = 0.40

REPAIR = {
    "core": "Python core (Ch. 5-6; numbers 7.8-7.9)",
    "gotchas": "gotchas (Ch. 7, 23)",
    "complexity": "Big-O (Ch. 8)",
    "coding": "playbook + hashing drills (Ch. 2, 9)",
}

TRACK_WEEKS = {  # same tables as Chapter 1, ex06
    "S": ("Track part 1: Ch. 29-30", "Track part 2: Ch. 28, 31-32"),
    "M": ("Track part 1: Ch. 33-35", "Track part 2: Ch. 36-37"),
    "L": ("Track part 1: Ch. 38-40", "Track part 2: Ch. 41-43"),
}
STANDARD = [  # week texts identical to Chapter 1, ex06 and the outline's 8-week plan
    "Playbook, Big-O, Python essentials, gotchas, arrays/strings/hashing (Ch. 1-9)",
    "Two pointers, sliding window, prefix sums, binary search, sorting (Ch. 10-11)",
    "Stacks, queues, linked lists, recursion and trees (Ch. 12-14)",
    "Heaps, top-K, graphs (Ch. 15-17) + mock #1",
    "Backtracking, DP, greedy, intervals (Ch. 18-21)",
    "TRACK-1",
    "TRACK-2",
    "Two full mocks, weak-area repair, revision (Ch. 44-48)",
]
FAST_WEEK_1 = "Skim Part I; playbook, Big-O, arrays/strings/hashing (Ch. 2, 8-9)"
CRASH = [
    "Patterns and hashing (Ch. 2, 8-11); skim Part I via the diagnostic",
    "Trees, graphs, heaps (Ch. 14-17)",
    "DP, backtracking (Ch. 18-19) + role track highlights",
    "Mocks and weak-area repair (Ch. 44-48)",
]
FOUNDATIONS = [
    "Setup and Python syntax (Ch. 4-5)",
    "Collections and the stdlib toolbox (Ch. 6)",
    "Gotchas and Big-O (Ch. 7-8)",
    "Basic DSA warm-up: arrays, strings, hashing (Ch. 9)",
]


def percentages(scores: dict[str, int]) -> dict[str, float]:
    raise NotImplementedError("TODO")


def place(scores: dict[str, int]) -> dict:
    raise NotImplementedError("TODO")


def choose_plan(path: str, weeks_available: int) -> tuple[str, bool]:
    raise NotImplementedError("TODO")


def weekly_plan(scores: dict[str, int], track: str, weeks_available: int) -> dict:
    raise NotImplementedError("TODO")


CANDIDATES = [  # (label, scores, track, weeks available)
    ("strong SWE", {"core": 8, "gotchas": 7, "complexity": 11, "coding": 8}, "S", 4),
    ("sample sheet", {"core": 7, "gotchas": 4, "complexity": 9, "coding": 6}, "L", 8),
    ("career changer", {"core": 3, "gotchas": 2, "complexity": 4, "coding": 0}, "M", 12),
]


def main() -> None:
    for label, scores, track, weeks in CANDIDATES:
        pct = percentages(scores)
        res = weekly_plan(scores, track, weeks)
        print(f"{label}: " + " ".join(f"{a}={pct[a]:.0%}" for a in AREAS)
              + f" overall={res['overall']:.0%}")
        print(f"  path={res['path']} weak={res['weak']} track={track} "
              f"weeks={weeks} -> plan={res['plan']} warning={res['warning']}")
        for n, focus in res["weeks"]:
            if n == 1 or "Track part" in focus or "highlights" in focus or "retake" in focus:
                print(f"    Week {n}: {focus}")
        print(f"    ({len(res['weeks'])} weeks in total)")
    print()
    print("Edge cases:")
    print("  choose_plan('full', 5) ->", choose_plan("full", 5))
    print("  choose_plan('foundations', 10) ->", choose_plan("foundations", 10))
    boundary = {"core": 6, "gotchas": 6, "complexity": 9, "coding": 6}  # exactly 75 % each
    print("  all areas exactly 75% ->", place(boundary)["path"])
    try:
        place({"core": 9})
    except ValueError as exc:
        print("  bad score ->", exc)


if __name__ == "__main__":
    main()
