"""
Exercise 06 — Study-Plan Builder                                  [Tier: ★ Core]
Chapter 01 · Pattern: decision table + templating · Target time: 25 min

Problem
-------
The course offers three plans (see "Study Plans" in the outline):
- "crash-4"        : 4 weeks, ~15 h/week, for experienced engineers on the fast track;
- "standard-8"     : 8 weeks, 10-12 h/week;
- "foundations-12" : 12 weeks, 6-8 h/week — 4 weeks of Python essentials, then standard-8.

Write `choose_plan(weeks_available, hours_per_week, fast_track)`:
1. total = weeks_available * hours_per_week. If total < 40 raise ValueError("not enough time").
2. If fast_track and weeks_available < 8            -> "crash-4".
3. Else if weeks_available >= 12 and not fast_track -> "foundations-12".
4. Else if weeks_available >= 8                     -> "standard-8".
5. Else (not fast_track, fewer than 8 weeks)        -> "crash-4", but with a warning flag.
Return (plan_name, warning: bool).

Write `build_plan(plan_name, track)` that returns a list of (week_number, focus) tuples using
the tables below; weeks 6 and 7 of the standard plan are track-specific (TRACK_WEEKS).

Examples
--------
>>> choose_plan(6, 15, fast_track=True)
('crash-4', False)
>>> build_plan("standard-8", "L")[5]
(6, 'Track part 1: Ch. 38-40')

Constraints
-----------
- track is "S", "M" or "L"; anything else raises ValueError.


Hints
-----
- Build the standard plan as a list, then replace weeks 6 and 7 by track.
- foundations-12 = FOUNDATION_WEEKS + the standard plan renumbered from week 5.

Follow-ups
----------
- How would you shift the plan if your interview date moved one week earlier?
"""
from __future__ import annotations

STANDARD_WEEKS = [
    "Playbook, Big-O, Python essentials, gotchas, arrays/strings/hashing (Ch. 1-9)",
    "Two pointers, sliding window, prefix sums, binary search, sorting (Ch. 10-11)",
    "Stacks, queues, linked lists, recursion and trees (Ch. 12-14)",
    "Heaps, top-K, graphs (Ch. 15-17) + mock #1",
    "Backtracking, DP, greedy, intervals (Ch. 18-21)",
    "TRACK-1",
    "TRACK-2",
    "Two full mocks, weak-area repair, revision (Ch. 44-48)",
]

TRACK_WEEKS = {
    "S": ("Track part 1: Ch. 29-30", "Track part 2: Ch. 28, 31-32"),
    "M": ("Track part 1: Ch. 33-35", "Track part 2: Ch. 36-37"),
    "L": ("Track part 1: Ch. 38-40", "Track part 2: Ch. 41-43"),
}

CRASH_WEEKS = [
    "Patterns and hashing (Ch. 2, 8-11); skim Part I via the diagnostic",
    "Trees, graphs, heaps (Ch. 14-17)",
    "DP, backtracking (Ch. 18-19) + role track highlights",
    "Mocks and weak-area repair (Ch. 44-48)",
]

FOUNDATION_WEEKS = [
    "Setup and Python syntax (Ch. 4-5)",
    "Collections and the stdlib toolbox (Ch. 6)",
    "Gotchas and Big-O (Ch. 7-8)",
    "Basic DSA warm-up: arrays, strings, hashing (Ch. 9)",
]


def choose_plan(weeks_available: int, hours_per_week: int, fast_track: bool) -> tuple[str, bool]:
    """Pick a plan name and whether to warn that it is a stretch."""
    raise NotImplementedError("TODO")


def build_plan(plan_name: str, track: str) -> list[tuple[int, str]]:
    """Week-by-week focus list."""
    raise NotImplementedError("TODO")


def main() -> None:
    scenarios = [(6, 15, True, "S"), (10, 11, False, "M"), (12, 7, False, "L"), (5, 10, False, "S")]
    for weeks, hours, fast, track in scenarios:
        plan, warn = choose_plan(weeks, hours, fast)
        flag = "  (warning: tight timeline, consider postponing)" if warn else ""
        print(f"{weeks} weeks x {hours} h, fast_track={fast}, track {track} -> {plan}{flag}")
    print("\nstandard-8 for track L:")
    for week, focus in build_plan("standard-8", "L"):
        print(f"  Week {week}: {focus}")
    try:
        choose_plan(3, 10, True)
    except ValueError as exc:
        print("\nError:", exc)


if __name__ == "__main__":
    main()
