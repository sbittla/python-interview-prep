"""
Exercise 06 — Take-Home Scope Planner                              [Tier: ○ Reference]
Chapter 32 · Pattern: MoSCoW prioritisation under a time box · Target time: 20 min

Problem
-------
A take-home says "about 3 hours". Before writing code, list the tasks, give
each an estimate in minutes and a priority (must / should / could), and plan.

plan(tasks, budget_min, reserve_pct=25) -> Plan:
- reserve = budget_min * reserve_pct // 100 minutes are kept for the README,
  a final test run and slack; the rest is the build budget.
- All "must" tasks go in first, in the given order. If they do not fit the
  build budget, raise ScopeError("must tasks need X min, build budget is Y min"):
  that is the moment to email the recruiter, not to skip the README.
- Then "should", then "could" tasks, in the given order: each one goes in if
  it still fits (greedy; a later small task may fit after a big one is skipped).
- Plan has in_scope, deferred (the tasks left out), reserve, used and slack (build
  budget minus used).

readme_scope(plan) -> the "## Scope" section for the README: done items, then
"Not done (next steps)" with the deferred items and their estimates.

Examples
--------
>>> p = plan([Task("parse", 30, "must"), Task("json", 60, "could")], 80)
>>> [t.name for t in p.in_scope], [t.name for t in p.deferred], p.slack
(['parse'], ['json'], 30)

Constraints
-----------
- Whole minutes only (no floats); priorities other than must/should/could raise ValueError.

Hints
-----
- Validate priorities first; compute reserve with integer arithmetic (//).
- Sum the musts; raise ScopeError if they exceed the build budget.
- Then loop over ("should", "could") and over the tasks of that priority in
  order, adding each one that still fits.

Follow-ups
----------
- Optimal packing of shoulds/coulds is a 0/1 knapsack (→ §19.6); greedy by
  priority is what reviewers can follow, and estimates are too rough to
  justify more.
- Re-plan at the half-way mark with actual times.
"""
from __future__ import annotations

from dataclasses import dataclass, field

PRIORITIES = ("must", "should", "could")


class ScopeError(Exception):
    pass


@dataclass(frozen=True)
class Task:
    name: str
    minutes: int
    priority: str


@dataclass
class Plan:
    in_scope: list[Task] = field(default_factory=list)
    deferred: list[Task] = field(default_factory=list)
    reserve: int = 0
    used: int = 0
    slack: int = 0


def plan(tasks: list[Task], budget_min: int, reserve_pct: int = 25) -> Plan:
    raise NotImplementedError("TODO")


def readme_scope(p: Plan) -> str:
    raise NotImplementedError("TODO")


TASKS = [
    Task("parse + validate CSV", 40, "must"),
    Task("per-category totals", 20, "must"),
    Task("CLI with argparse", 25, "must"),
    Task("unit tests for core", 30, "must"),
    Task("JSON output", 15, "should"),
    Task("month filter", 15, "should"),
    Task("multi-currency", 60, "could"),
    Task("--strict flag", 10, "could"),
]


def show_tasks(tasks: list[Task]) -> None:
    for level in PRIORITIES:
        group = [t for t in tasks if t.priority == level]
        items = ", ".join(f"{t.name} {t.minutes}" for t in group)
        print(f"{level:<6} ({sum(t.minutes for t in group):>3} min): {items}")


def show_plan(tasks: list[Task], budget: int) -> Plan:
    p = plan(tasks, budget)
    musts = sum(t.minutes for t in tasks if t.priority == "must")
    extra = [t.name for t in p.in_scope if t.priority != "must"]
    print(f"budget {budget}: reserve {p.reserve}, build {budget - p.reserve}, musts {musts}, "
          f"slack {p.slack}")
    print(f"  added beyond musts: {extra}")
    print(f"  deferred: {[t.name for t in p.deferred]}")
    return p


def main() -> None:
    show_tasks(TASKS)
    show_plan(TASKS, 170)
    p = show_plan(TASKS, 180)
    print(readme_scope(p))
    print()
    try:
        plan(TASKS, 120)
    except ScopeError as exc:
        print("budget 120:", exc)
    print("empty task list:", plan([], 60))


if __name__ == "__main__":
    main()
