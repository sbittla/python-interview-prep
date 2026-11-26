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

Approach ladder
---------------
1. Brute force — a hand-written script per mock: ten files that drift from the catalogue.
2. Improved   — one template with the mock pasted in: drifts when the catalogue changes.
3. Optimal    — generate from the validated catalogue and the rubric data. O(L) in output lines.

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
    out = []
    for name, start, end in timebox(mock):
        out.append((start, name))
        if len(name) > 2 and name[1] == ":" and name[0].isupper():
            out.append((start + (end - start) * 40 // 100,
                        f"checkpoint {name[0]}: no plan stated yet? offer hint {name[0]}1"))
    return sorted(out, key=lambda c: c[0])


def script(mock: Mock) -> list[str]:
    if mock.rubric not in RUBRICS:
        raise ValueError(f"unknown rubric {mock.rubric!r}")
    rubric, section = RUBRICS[mock.rubric]
    out = [f"Mock {mock.id}: {mock.title} ({mock.minutes} min, rubric §{section})",
           f"Role: {mock.role}", "", "Interviewer files (do not share):"]
    out += [f"  {p['label']}: {p['path']}" for p in mock.problems]
    out += ["", "Read aloud:"]
    out += [f"  {p['label']} ({p['ref']}): {p['prompt']}" for p in mock.problems]
    out += ["", "Timeline:"]
    for minute, text in checkpoints(mock):
        cue = CUES.get(text)
        if cue is None and text[:2] in {f"{p['label']}:" for p in mock.problems}:
            cue = "read the prompt; answer questions; do not volunteer constraints"
        out.append(f"  {minute:02d}:00 {text}" + (f" - {cue}" if cue else ""))
    out += ["", "Hints (one at a time, after ~3 min stuck; log each as HINT):"]
    out += [f"  {p['label']}{i}. {h}" for p in mock.problems for i, h in enumerate(p["hints"], 1)]
    out += ["", "Follow-ups:"] + [f"  - {f}" for f in mock.followups]
    out += ["", "Strong looks like:"] + [f"  - {s}" for s in mock.strong]
    out += ["", "Scoring sheet (" + " ".join(f"{k}={v}" for k, v in SCALE.items()) + "):"]
    out += [f"  [ ] {label} ({w})" for _, label, w in rubric]
    return out


def main() -> None:
    mocks = by_id(load_mocks())
    print("\n".join(script(mocks["S2"])))
    print("\n--- L3 uses the AI-assisted rubric ---")
    lines = script(mocks["L3"])
    start = lines.index(next(line for line in lines if line.startswith("Scoring sheet")))
    print("\n".join([lines[0]] + lines[start:]))


if __name__ == "__main__":
    main()
