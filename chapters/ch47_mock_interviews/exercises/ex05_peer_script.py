"""
Exercise 05 — Peer-Interviewer Script Generator             [Tier: ○ Reference]
Chapter 47 · Pattern: template filled from validated data · Target time: 20 min

Problem
-------
A peer who has never run a mock needs one page: what to read aloud, when to nudge,
which hints to give, what to ask at the end, and how to score. Build it from the
catalogue (Exercise 02) and the rubrics (Exercise 01), never from hand-copied text.

1. ``checkpoints(mock)`` -> [(minute, text)] sorted by minute: the start of every
   segment, plus for each problem segment (name "A: ...", "B: ...") a checkpoint at
   start + 40 % of its length (floor): "checkpoint A: no plan stated yet? offer hint A1".
2. ``script(mock)`` -> list of lines: header, the files only the interviewer opens,
   the prompt to read aloud for each problem, the timeline with cues, a hint ladder per
   problem, follow-ups, what strong looks like, and a scoring sheet with the right
   rubric (``"ai"`` -> §47.4, else §47.3) and every weight. Unknown rubric: ValueError.

Examples
--------
>>> m = by_id(load_mocks())["S1"]
>>> checkpoints(m)[:3]
[(0, 'intro'), (5, 'A: merge two sorted lists'), (10, 'checkpoint A: no plan stated yet? offer hint A1')]

Constraints
-----------
- Deterministic text; everything comes from the catalogue and the rubrics.

Hints
-----
- A problem segment is named "A: ...", "B: ...": its checkpoint minute is
  start + (end - start) * 40 // 100.
- Sort by minute only: ``sorted`` is stable, so a segment start stays first.
- Line formats the tests look for: "Mock S2: <title> (<n> min, rubric §47.3)",
  "  <label> (<ref>): <prompt>", "  MM:00 <text>[ - <cue>]", "  A1. <hint>",
  "  - <follow-up>", "  - <strong>", "  [ ] <label> (<weight>)".
- Unknown rubric: ValueError.

Follow-ups
----------
- Add a "candidate is ahead of time" branch: which follow-up to start early.
- Emit the scoring sheet as CSV rows that Exercise 04 can read.
"""
from __future__ import annotations

from ex01_rubric_scorer import AI_RUBRIC, CODING_RUBRIC, SCALE
from ex02_mock_planner import Mock, by_id, load_mocks, timebox

RUBRICS = {"coding": (CODING_RUBRIC, "47.3"), "ai": (AI_RUBRIC, "47.4")}
CUES = {
    "intro": "introduce yourself; say the length; ask them to think aloud",
    "closing": "stop coding; ask the follow-ups; leave time for their questions",
    "API and requirements": "ask for the API and complexity targets before any code",
    "plan and decompose": "ask for the plan and stop conditions before the first prompt",
    "walkthrough": "pick three lines; ask why each is there and how it was checked",
}


def checkpoints(mock: Mock) -> list[tuple[int, str]]:
    raise NotImplementedError("TODO")


def script(mock: Mock) -> list[str]:
    raise NotImplementedError("TODO")


def main() -> None:
    mocks = by_id(load_mocks())
    print("\n".join(script(mocks["S2"])))
    print("\n--- L3 uses the AI-assisted rubric ---")
    lines = script(mocks["L3"])
    start = lines.index(next(line for line in lines if line.startswith("Scoring sheet")))
    print("\n".join([lines[0]] + lines[start:]))


if __name__ == "__main__":
    main()
