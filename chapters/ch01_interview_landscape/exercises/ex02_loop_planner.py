"""
Exercise 02 — Interview-Loop Planner                              [Tier: ★ Core]
Chapter 01 · Pattern: proportional allocation (largest remainder) · Target time: 25 min

Problem
-------
A recruiter describes your loop as a list of rounds, e.g.
    [("phone_screen", 1), ("coding", 2), ("system_design", 1), ("behavioural", 1)]
Each round type has a preparation weight in ROUND_WEIGHT (coding rounds need more practice than
a behavioural round). Given `total_hours` of study time, write
`plan_hours(rounds, total_hours)` that returns {round_type: hours} where

1. raw share = total_hours * weight * count / sum(weight * count over all rounds);
2. every round type gets the floor of its raw share;
3. leftover hours go one at a time to the types with the largest fractional remainder
   (ties broken alphabetically) — the "largest remainder" method, so the hours always sum
   exactly to total_hours;
4. unknown round types raise ValueError.

Then `weekly_schedule(rounds, weeks, hours_per_week)` returns a list of strings, one per week
("Week k: type=h, ..." with zero-hour types omitted). Every week must hold exactly
hours_per_week hours: each week, split hours_per_week over the types in proportion to the hours
each type still has *remaining*, again with largest remainder, then subtract.

Examples
--------
>>> plan_hours([("coding", 2), ("behavioural", 1)], 10)
{'behavioural': 1, 'coding': 9}

Constraints
-----------
- 1 <= total_hours <= 10_000, counts >= 1. Return keys in sorted order.


Hints
-----
- Use integer arithmetic for the remainders to avoid float ties: numerator % denominator.
- sorted(types, key=lambda t: (-remainder[t], t)) gives the leftover order.
- Splitting each type over the weeks independently looks fine per type but lets week totals
  drift (13, 12, 11 instead of 12, 12, 12): the leftovers all land on week 1.

Follow-ups
----------
- How would you guarantee a minimum of 1 hour for every round type?
- How would you re-plan after week 1 if you fell behind?
"""
from __future__ import annotations

ROUND_WEIGHT = {
    "phone_screen": 2,
    "online_assessment": 3,
    "coding": 5,
    "practical": 4,
    "system_design": 4,
    "ml_coding": 5,
    "behavioural": 1,
}


def largest_remainder(weights: dict[str, int], total: int) -> dict[str, int]:
    """Split integer `total` proportionally to integer `weights`, summing exactly to total."""
    raise NotImplementedError("TODO")


def plan_hours(rounds: list[tuple[str, int]], total_hours: int) -> dict[str, int]:
    """Hours of preparation per round type."""
    raise NotImplementedError("TODO")


def weekly_schedule(rounds: list[tuple[str, int]], weeks: int, hours_per_week: int) -> list[str]:
    """One line per week: 'Week k: type=h, ...' (types with 0 hours omitted)."""
    raise NotImplementedError("TODO")


def main() -> None:
    swe_loop = [("phone_screen", 1), ("coding", 2), ("system_design", 1), ("behavioural", 1)]
    ml_loop = [("online_assessment", 1), ("ml_coding", 1), ("coding", 1), ("behavioural", 1)]
    print("SWE loop, 40 h:", plan_hours(swe_loop, 40))
    print("ML loop,  40 h:", plan_hours(ml_loop, 40))
    print("Sum check:", sum(plan_hours(swe_loop, 37).values()) == 37)
    print("\nSWE loop over 3 weeks x 12 h:")
    for line in weekly_schedule(swe_loop, 3, 12):
        print("  " + line)
    try:
        plan_hours([("trivia", 1)], 10)
    except ValueError as exc:
        print("\nError:", exc)


if __name__ == "__main__":
    main()
