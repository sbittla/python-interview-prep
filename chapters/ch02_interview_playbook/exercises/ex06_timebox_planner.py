"""
Exercise 06 — Timebox Planner for 45- and 60-Minute Rounds  [Tier: ○ Reference]
Chapter 02 · Pattern: interview method (time management) · Target time: 15 min

Problem
-------
Split a coding round into phases and tell the candidate, at any minute,
whether they are on schedule and what to do if not.

plan(total, intro=5, closing=5) -> list of (phase, start, end) minutes.
  The working time W = total - intro - closing is shared by four phases with
  weights 15 / 25 / 40 / 20 percent:
      "clarify+examples", "brute+optimise", "code", "test"
  Minutes are whole numbers: take the floor of each share, then give the
  leftover minutes one by one to the phases with the largest fractional
  part (ties: earlier phase first). "intro" comes first and "closing" last.

checkpoint(schedule, minute, phase) -> advice string. `phase` is the phase the
  candidate is in now. If `minute` is past that phase's end, say how many
  minutes behind and give the phase's recovery action; otherwise "on track".

Examples
--------
>>> [(p, s, e) for p, s, e in plan(45)][1:5]
[('clarify+examples', 5, 10), ('brute+optimise', 10, 19), ('code', 19, 33), ('test', 33, 40)]

Constraints
-----------
- W must be at least 4 minutes (ValueError otherwise).
- Phase lengths always sum to total exactly.

Hints
-----
- Use integer arithmetic: floor = work * w // 100, remainder = work * w % 100.
- Hand out the leftover minutes to the largest remainders, ties to the
  earlier phase.
- checkpoint: find the phase's end; behind = minute - end when positive.

Follow-ups
----------
- Two problems in one round: plan each with half the working time.
- A round with a 15-minute behavioural block: pass intro=15.
"""
from __future__ import annotations

PHASES = [("clarify+examples", 15), ("brute+optimise", 25), ("code", 40), ("test", 20)]
RECOVERY = {
    "intro": "keep introductions to two sentences and move to the problem",
    "clarify+examples": "state your assumptions aloud and move on",
    "brute+optimise": "code the best idea you have now; mention the better one",
    "code": "stub helper functions, finish the main path, fill in later",
    "test": "trace one normal and one edge case, then list the rest aloud",
    "closing": "ask one question that matters to you",
}


def plan(total: int, intro: int = 5, closing: int = 5) -> list[tuple[str, int, int]]:
    raise NotImplementedError("TODO")


def checkpoint(schedule: list[tuple[str, int, int]], minute: int, phase: str) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    for total in (45, 60):
        print(f"{total}-minute round:")
        for name, start, end in plan(total):
            print(f"  {start:>2}-{end:<2} {name:<17} ({end - start} min)")
    s45 = plan(45)
    print("\nCheckpoints in a 45-minute round:")
    for minute, phase in [(9, "clarify+examples"), (14, "clarify+examples"),
                          (24, "brute+optimise"), (36, "code")]:
        print(f"  minute {minute:>2}, still in {phase:<17}: {checkpoint(s45, minute, phase)}")


if __name__ == "__main__":
    main()
