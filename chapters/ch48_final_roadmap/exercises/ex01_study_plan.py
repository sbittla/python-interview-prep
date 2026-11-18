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

Follow-ups
----------
- Add hours per week and warn when the quota exceeds ~1 problem per 40 minutes.
- Export the plan as CSV for a spreadsheet tracker.
- Insert a buffer week automatically when the interview date is further away than the plan.
"""
from __future__ import annotations
from dataclasses import dataclass
PLAN_NAMES = ('8-week', '4-week', '12-week', '6-week')
TRACKS = {'S': 'Software Engineering', 'M': 'Data / ML', 'L': 'GenAI / LLM'}
HOURS = {'8-week': '10-12 h/week', '4-week': '~15 h/week', '12-week': '6-8 h/week', '6-week': '10-12 h/week'}
TRACK_PART1 = {'S': [29, 30], 'M': [33, 34, 35], 'L': [38, 39, 40]}
TRACK_PART2 = {'S': [28, 31, 32], 'M': [36, 37], 'L': [41, 42, 43]}
TRACK_LABEL = {'S': ('Design-style problems, log/text processing, SQL', 'Concurrency, testing/debugging, take-home workflow'), 'M': ('NumPy, pandas/SQL, ML math and metrics', 'Classical ML from scratch, PyTorch training'), 'L': ('Tokenisation, attention/decoding, retrieval and RAG', 'Agents, production patterns, LLM system design')}

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

def standard_weeks(track: str, start: int=1) -> list[Week]:
    """The standard 8-week plan, numbered from ``start``."""
    raise NotImplementedError('TODO')

def crash_weeks(track: str) -> list[Week]:
    raise NotImplementedError('TODO')

def foundation_weeks() -> list[Week]:
    raise NotImplementedError('TODO')

def addon_weeks(track: str) -> list[Week]:
    raise NotImplementedError('TODO')

def build_plan(plan: str, track: str='S') -> list[Week]:
    raise NotImplementedError('TODO')

def total_problems(weeks: list[Week]) -> int:
    raise NotImplementedError('TODO')

def checkpoints(weeks: list[Week]) -> list[str]:
    raise NotImplementedError('TODO')

def _chapters(chs: list[int]) -> str:
    """Compress consecutive chapter numbers: [1,2,3,5] -> '1-3, 5'."""
    parts, start, prev = ([], chs[0], chs[0])
    for c in chs[1:] + [None]:
        if c is not None and c == prev + 1:
            prev = c
            continue
        parts.append(f'{start}' if start == prev else f'{start}-{prev}')
        if c is not None:
            start = prev = c
    return ', '.join(parts)

def render_plan(plan: str, track: str='S') -> str:
    raise NotImplementedError('TODO')

def main() -> None:
    for plan, track in [('8-week', 'S'), ('4-week', 'L'), ('12-week', 'M'), ('6-week', 'L')]:
        print(render_plan(plan, track))
        print()
    print('Week 6-7 chapters by track:')
    for t in sorted(TRACKS):
        weeks = build_plan('8-week', t)
        print(f'  {t}: week 6 -> {weeks[5].chapters}, week 7 -> {weeks[6].chapters}')
    for bad in [('10-week', 'S'), ('8-week', 'X'), ('6-week', 'S')]:
        try:
            build_plan(*bad)
        except ValueError as exc:
            print(f'build_plan{bad} -> ValueError: {exc}')
if __name__ == '__main__':
    main()
