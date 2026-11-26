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

Approach ladder
---------------
1. Brute force — read the log by eye: slow, and people forgive their own silences.
2. Improved   — regex per question ("is there an ASK?") rescanning the text: O(Q·n),
   and malformed lines slip through silently.
3. Optimal    — parse once into validated events, then one pass computes every
   metric. O(n) time, O(n) space.

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
LINE_RE = re.compile(r"^(\d{2}):([0-5]\d) ([A-Z_]+)(?: (.*))?$")
RUN_RE = re.compile(r"^(\d+)/(\d+)\b")


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
    events: list[Event] = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = LINE_RE.match(line)
        if not m:
            raise ValueError(f"line {n}: expected 'MM:SS EVENT [detail]': {line!r}")
        t, kind, detail = int(m[1]) * 60 + int(m[2]), m[3], m[4] or ""
        if kind not in KINDS:
            raise ValueError(f"line {n}: unknown event {kind}")
        if kind == "RUN":
            r = RUN_RE.match(detail)
            if not r or int(r[2]) < 1 or int(r[1]) > int(r[2]):
                raise ValueError(f"line {n}: RUN needs passed/total, got {detail!r}")
        if events and t < events[-1].t:
            raise ValueError(f"line {n}: time goes backwards")
        if events and events[-1].kind == "END":
            raise ValueError(f"line {n}: event after END")
        if kind == "START" and events:
            raise ValueError(f"line {n}: START must be the first event")
        if not events and kind != "START":
            raise ValueError(f"line {n}: log must begin with START")
        events.append(Event(t, kind, detail))
    if not events or events[-1].kind != "END":
        raise ValueError("log must end with END")
    return events


def analyse(events: list[Event], silence: int = 180) -> Analysis:
    def first(kind, pred=lambda e: True):
        return next((e.t for e in events if e.kind == kind and pred(e)), None)

    def passed(e):
        p, t = RUN_RE.match(e.detail).groups()
        return p == t

    gap, gap_start = 0, events[0].t
    for a, b in zip(events, events[1:]):
        if b.t - a.t > gap:
            gap, gap_start = b.t - a.t, a.t
    count = lambda kind: sum(e.kind == kind for e in events)
    res = Analysis(events[-1].t - events[0].t, first("ASK"), first("CODE_START"),
                   count("RUN"), first("RUN", passed), count("HINT"), count("TEST_ADDED"),
                   (gap, gap_start))

    code = res.first_code if res.first_code is not None else events[-1].t
    before = lambda kind: any(e.kind == kind and e.t <= code for e in events)
    if not before("ASK"):
        res.flags.append(("clarifying", "coded before asking any question"))
    if not before("PLAN"):
        res.flags.append(("approach", "no approach stated before coding"))
    if res.hints >= 2:
        res.flags.append(("approach", f"{res.hints} hints used"))
    if not before("COMPLEXITY"):
        res.flags.append(("complexity", "complexity not stated before coding"))
    if res.first_green is None:
        res.flags.append(("correctness", "no fully passing run"))
    if res.tests_added == 0:
        res.flags.append(("testing", "no tests of your own added"))
    if gap > silence:
        res.flags.append(("communication", f"silent {mmss(gap)} from {mmss(gap_start)}"))
    return res


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
