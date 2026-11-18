"""
Exercise 01 — Study-Plan Generator                            [Tier: ★ Core]
Chapter 48 · Pattern: data modelling + formatting · Target time: 25 min

Problem
-------
The course offers four study plans (see the Study Plans section of the outline):

* ``8-week``  — the standard plan, 10–12 h/week, weeks 6–7 depend on the track (S, M, L).
* ``4-week``  — crash plan for experienced engineers (~15 h/week).
* ``12-week`` — foundations plan: four weeks of Python essentials and basic DSA, then the
  standard 8-week plan (6–8 h/week).
* ``6-week``  — role add-on for people with strong DSA moving to ML/LLM work
  (Parts VI and VII + Part V + two mocks).

Write ``build_plan(plan, track)`` that returns a list of ``Week`` records (week number, focus,
chapters, problem quota, checkpoint) and ``render_plan`` that prints a week-by-week schedule.
Also return the total problem quota and the list of checkpoints.

Examples
--------
>>> [w.chapters for w in build_plan("8-week", "S")][5]
[29, 30]
>>> total_problems(build_plan("8-week", "S"))
119

Constraints
-----------
- ``plan`` is one of ``PLAN_NAMES``; ``track`` is one of ``"S"``, ``"M"``, ``"L"``.
- Unknown plan or track -> ``ValueError`` with a helpful message.
- Output must be deterministic (no "today" — plans are relative week numbers).

Hints
-----
- Store each plan as data (a list of tuples) and keep the rendering separate.
- The track only changes weeks 6–7 of the 8-week plan (and the role weeks of the other plans).
- The 12-week plan is "4 foundation weeks" + the 8-week plan renumbered from week 5.

Approach ladder
---------------
1. Brute force — one giant ``print`` per plan. Impossible to test or reuse.
2. Improved   — dict of plan name -> list of rows; render with f-strings.
3. Optimal    — immutable ``Week`` dataclass, plan builders that compose (12-week reuses
   8-week), validation up front. O(W) to build and render W weeks.

Follow-ups
----------
- Add hours per week and warn when the quota exceeds ~1 problem per 40 minutes.
- Export the plan as CSV for a spreadsheet tracker.
- Insert a buffer week automatically when the interview date is further away than the plan.
"""
from __future__ import annotations

from dataclasses import dataclass

PLAN_NAMES = ("8-week", "4-week", "12-week", "6-week")
TRACKS = {"S": "Software Engineering", "M": "Data / ML", "L": "GenAI / LLM"}
HOURS = {"8-week": "10-12 h/week", "4-week": "~15 h/week", "12-week": "6-8 h/week",
         "6-week": "10-12 h/week"}

# Track-specific chapters for weeks 6 and 7 of the standard plan (from the outline).
TRACK_PART1 = {"S": [29, 30], "M": [33, 34, 35], "L": [38, 39, 40]}
TRACK_PART2 = {"S": [28, 31, 32], "M": [36, 37], "L": [41, 42, 43]}
TRACK_LABEL = {
    "S": ("Design-style problems, log/text processing, SQL",
          "Concurrency, testing/debugging, take-home workflow"),
    "M": ("NumPy, pandas/SQL, ML math and metrics",
          "Classical ML from scratch, PyTorch training"),
    "L": ("Tokenisation, attention/decoding, retrieval and RAG",
          "Agents, production patterns, LLM system design"),
}


@dataclass(frozen=True)
class Week:
    week: int
    focus: str
    chapters: list[int]
    problems: int
    checkpoint: str
    labs: bool = False


def _check(plan: str, track: str) -> None:
    if plan not in PLAN_NAMES:
        raise ValueError(f"unknown plan {plan!r}; choose one of {', '.join(PLAN_NAMES)}")
    if track not in TRACKS:
        raise ValueError(f"unknown track {track!r}; choose one of {', '.join(sorted(TRACKS))}")


def standard_weeks(track: str, start: int = 1) -> list[Week]:
    """The standard 8-week plan, numbered from ``start``."""
    p1, p2 = TRACK_LABEL[track]
    rows = [
        ("Playbook, Big-O, Python essentials, gotchas, arrays/strings/hashing",
         list(range(1, 10)), 15, "Diagnostic retake; gotchas quiz", False),
        ("Two pointers, sliding window, prefix sums, binary search, sorting",
         [10, 11], 18, "3 problems in 60 min", False),
        ("Stacks, queues, linked lists, recursion and trees",
         [12, 13, 14], 18, "Pattern-recognition drill", False),
        ("Heaps, top-K, graphs, tries and intervals",
         [15, 16, 17], 18, "Mock #1 (rubric-scored)", False),
        ("Backtracking, DP, greedy, math and bits",
         [18, 19, 20, 21], 18, "Spaced revisit of weeks 1-3", False),
        (f"Track part 1 - {p1}", TRACK_PART1[track], 10, "Mini project", True),
        (f"Track part 2 - {p2}", TRACK_PART2[track], 10, "AI-assisted round practice", True),
        ("Two full mocks, weak-area repair, cheat-sheet revision",
         [44, 45, 46, 47, 48], 12, "90-min final assessment", False),
    ]
    return [Week(start + i, f, c, p, k, lab) for i, (f, c, p, k, lab) in enumerate(rows)]


def crash_weeks(track: str) -> list[Week]:
    role = TRACK_PART1[track] + TRACK_PART2[track]
    return [
        Week(1, "Diagnostic, playbook, gotchas, patterns and hashing",
             [2, 3, 7, 8, 9, 10, 11], 25, "Diagnostic decides what to skip"),
        Week(2, "Stacks, linked lists, trees, heaps, graphs, tries",
             [12, 13, 14, 15, 16, 17], 25, "3 problems in 60 min"),
        Week(3, "DP, backtracking, greedy + role track",
             [18, 19, 20] + role, 22, "Mock #1 (rubric-scored)", True),
        Week(4, "Mocks, weak-area repair, final roadmap",
             [44, 45, 46, 47, 48], 15, "Two full mocks + 90-min assessment"),
    ]


def foundation_weeks() -> list[Week]:
    return [
        Week(1, "Landscape, playbook, setup, syntax and functions",
             [1, 2, 3, 4, 5], 8, "Diagnostic test (baseline)"),
        Week(2, "Collections, stdlib toolbox, gotchas",
             [6, 7], 10, "Gotchas quiz >= 80%"),
        Week(3, "Big-O primer, arrays, strings, hashing",
             [8, 9], 12, "Estimate complexity of 10 snippets"),
        Week(4, "Iterators, OOP basics, exceptions and files",
             [23, 24, 26], 10, "Diagnostic retake; choose fast or full path"),
    ]


def addon_weeks(track: str) -> list[Week]:
    if track == "S":
        raise ValueError("the 6-week add-on is for tracks M and L (moving to ML/LLM roles)")
    return [
        Week(1, "NumPy, pandas/SQL, ML math and metrics", [33, 34, 35], 10, "Metrics from scratch", True),
        Week(2, "Classical ML from scratch, PyTorch", [36, 37], 10, "Debug a broken training loop", True),
        Week(3, "Tokenisation, attention and decoding", [38, 39], 8, "Mini GPT forward pass", True),
        Week(4, "Retrieval/RAG, agents, production patterns", [40, 41, 42], 8, "Mini RAG + eval harness", True),
        Week(5, "Practical rounds and LLM system design", [29, 30, 31, 32, 43], 10, "Code-review exercise"),
        Week(6, "Two mocks, AI-assisted practice, roadmap", [44, 46, 47, 48], 6, "Two rubric-scored mocks"),
    ]


def build_plan(plan: str, track: str = "S") -> list[Week]:
    _check(plan, track)
    if plan == "8-week":
        return standard_weeks(track)
    if plan == "4-week":
        return crash_weeks(track)
    if plan == "12-week":
        return foundation_weeks() + standard_weeks(track, start=5)
    return addon_weeks(track)


def total_problems(weeks: list[Week]) -> int:
    return sum(w.problems for w in weeks)


def checkpoints(weeks: list[Week]) -> list[str]:
    return [f"W{w.week}: {w.checkpoint}" for w in weeks]


def _chapters(chs: list[int]) -> str:
    """Compress consecutive chapter numbers: [1,2,3,5] -> '1-3, 5'."""
    parts, start, prev = [], chs[0], chs[0]
    for c in chs[1:] + [None]:
        if c is not None and c == prev + 1:
            prev = c
            continue
        parts.append(f"{start}" if start == prev else f"{start}-{prev}")
        if c is not None:
            start = prev = c
    return ", ".join(parts)


def render_plan(plan: str, track: str = "S") -> str:
    weeks = build_plan(plan, track)
    lines = [f"{plan} plan | track {track} ({TRACKS[track]}) | {HOURS[plan]}",
             f"{'Wk':>2}  {'Chapters':<18} {'Probs':>5}  Focus / checkpoint"]
    for w in weeks:
        quota = f"{w.problems}+L" if w.labs else str(w.problems)
        lines.append(f"{w.week:>2}  {_chapters(w.chapters):<18} {quota:>5}  {w.focus}")
        lines.append(f"{'':>2}  {'':<18} {'':>5}  -> checkpoint: {w.checkpoint}")
    lines.append(f"Total problems: {total_problems(weeks)} (+L = plus labs)")
    return "\n".join(lines)


def main() -> None:
    for plan, track in [("8-week", "S"), ("4-week", "L"), ("12-week", "M"), ("6-week", "L")]:
        print(render_plan(plan, track))
        print()
    print("Week 6-7 chapters by track:")
    for t in sorted(TRACKS):
        weeks = build_plan("8-week", t)
        print(f"  {t}: week 6 -> {weeks[5].chapters}, week 7 -> {weeks[6].chapters}")
    for bad in [("10-week", "S"), ("8-week", "X"), ("6-week", "S")]:
        try:
            build_plan(*bad)
        except ValueError as exc:
            print(f"build_plan{bad} -> ValueError: {exc}")


if __name__ == "__main__":
    main()
