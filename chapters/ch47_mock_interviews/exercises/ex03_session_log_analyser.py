"""
Exercise 03 — Mock Session Log Analyser                    [Tier: ★ Core]
Chapter 47 · Pattern: parse, validate, then single-pass metrics · Target time: 30 min

Problem
-------
During a mock the observer (or you, replaying a recording) logs one event per line:

    MM:SS EVENT [detail]          e.g.  "06:40 CODE_START" or "13:50 RUN 4/5"

EVENT is one of START, ASK, SAY, PLAN, COMPLEXITY, CODE_START, RUN, HINT, TEST_ADDED,
BUG_FOUND, END. Blank lines and lines starting with "#" are ignored. RUN's detail is
"passed/total". Implement

1. ``parse_log(text) -> list[Event]``. Raise ValueError("line N: ...") for a bad
   timestamp or event, a RUN without a valid p/t (0 <= p <= t, t >= 1), a time that
   goes backwards, or a log that does not start with START and end with END (exactly
   one of each).
2. ``analyse(events) -> Analysis`` with: duration, first ASK, first CODE_START, number
   of RUNs, first fully passing RUN, hints, own tests added, and the longest gap
   between consecutive events (seconds, and when it started).
3. Flags, each tagged with the §47.3 rubric key it is evidence for:
   - clarifying:    no ASK before CODE_START
   - approach:      no PLAN before CODE_START; 2 or more HINTs
   - complexity:    no COMPLEXITY before CODE_START
   - correctness:   no fully passing RUN
   - testing:       no TEST_ADDED
   - communication: a gap longer than ``silence`` seconds (default 180)
   Flags are evidence for the scorer, not a score: a human still rates 0-4.

Examples
--------
>>> a = analyse(parse_log("00:00 START\\n00:30 ASK n?\\n01:00 CODE_START\\n05:00 RUN 2/2\\n06:00 END"))
>>> a.first_green, [k for k, _ in a.flags]
(300, ['approach', 'complexity', 'testing', 'communication'])

Constraints
-----------
- Stdlib only; times are minutes 00-99 and seconds 00-59.

Hints
-----
- One regex per line: two-digit minutes, seconds 00-59, an upper-case event, optional detail.
- Check the order rules while parsing: START first, nothing after END, times never decrease.
- "Before code" means at or before the CODE_START time (or END if there is none).
- The longest gap is a max over ``zip(events, events[1:])``; keep the first maximum.
- Append flags in the order listed in the problem; the tests compare the list.

Follow-ups
----------
- Time from first HINT to the next passing RUN (how well the hint was used).
- Merge logs from two observers and report disagreements.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

LOGS = Path(__file__).resolve().parent.parent / "data" / "logs"
KINDS = {"START", "ASK", "SAY", "PLAN", "COMPLEXITY", "CODE_START", "RUN", "HINT",
         "TEST_ADDED", "BUG_FOUND", "END"}


@dataclass(frozen=True)
class Event:
    t: int
    kind: str
    detail: str


@dataclass
class Analysis:
    duration: int
    first_ask: int | None
    first_code: int | None
    runs: int
    first_green: int | None
    hints: int
    tests_added: int
    longest_gap: tuple[int, int]          # (seconds, start time)
    flags: list[tuple[str, str]] = field(default_factory=list)


def mmss(t: int) -> str:
    return f"{t // 60:02d}:{t % 60:02d}"


def parse_log(text: str) -> list[Event]:
    raise NotImplementedError("TODO")


def analyse(events: list[Event], silence: int = 180) -> Analysis:
    raise NotImplementedError("TODO")


def summary(name: str, a: Analysis) -> str:
    opt = lambda t: "-" if t is None else mmss(t)
    lines = [f"{name}: {mmss(a.duration)} total, first question {opt(a.first_ask)}, "
             f"code {opt(a.first_code)}, first green {opt(a.first_green)}",
             f"  runs={a.runs} hints={a.hints} own tests={a.tests_added} "
             f"longest gap={mmss(a.longest_gap[0])}"]
    lines += [f"  flag [{k}] {msg}" for k, msg in a.flags] or ["  no flags"]
    return "\n".join(lines)


def main() -> None:
    for path in sorted(LOGS.glob("*.log")):
        print(summary(path.stem, analyse(parse_log(path.read_text(encoding="utf-8")))))
    print("\nMalformed logs:")
    for bad in ("00:00 START\n00:10 RUN five\n00:20 END",
                "00:00 START\n02:00 ASK x\n01:00 SAY y\n03:00 END",
                "00:00 START\n00:30 ASK x"):
        try:
            parse_log(bad)
        except ValueError as exc:
            print("  ValueError:", exc)


if __name__ == "__main__":
    main()
