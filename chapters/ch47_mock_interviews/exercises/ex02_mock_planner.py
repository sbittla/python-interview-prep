"""
Exercise 02 — Mock Catalogue, Time Boxes and a Seeded Rotation   [Tier: ◆ Extended]
Chapter 47 · Pattern: validated catalogue + round-robin over shuffled queues · Target time: 30 min

Problem
-------
``data/mocks.json`` holds the ten mocks of §47.2. Each has an id, a track ("SWE",
"Data/ML", "GenAI/LLM"), a rubric ("coding" or "ai"), a length in minutes, a list of
[segment, minutes] pairs and the problems it uses (each with a repo ``path``, a
short ``prompt`` to read aloud and graded ``hints``).

1. ``load_mocks(path)`` -> list of ``Mock``, validated: ids unique; segments sum to
   ``minutes``; every problem path exists under the repository root and has a prompt
   and hints; the catalogue has
   exactly 4 SWE, 3 Data/ML and 3 GenAI/LLM mocks. Raise ValueError otherwise.
2. ``timebox(mock)`` -> [(segment, start, end)] in minutes from 0, contiguous.
3. ``rotation(mocks, tracks, sessions, seed)`` -> mock ids for ``sessions`` sessions.
   Sessions cycle through ``tracks`` in the given order. Each track draws from its own
   queue, a ``random.Random(seed)`` shuffle of its mock ids (shuffle tracks in the order
   given, one shared generator). An empty queue is refilled with a fresh shuffle; if the
   refill would start with the mock just served from that track, swap its first two
   entries, so no mock repeats back to back. Unknown tracks raise ValueError.
4. ``weekly(ids, per_week)`` -> list of weeks (lists of ids).

Examples
--------
>>> [s for s, _, _ in timebox(by_id(load_mocks())["S1"])]
['intro', 'A: merge two sorted lists', 'B: longest substring without repeats', 'closing']

Constraints
-----------
- Deterministic for a given seed; no clock, no global random state.

Hints
-----
- Build each Mock from the JSON, then check segments, rubric, problem files (with
  ``(root / path).is_file()``), prompts and hints, ids, and the per-track counts.
- timebox is a running sum over the segments.
- rotation: one ``random.Random(seed)``; shuffle each track's queue once, in the order
  tracks first appear in ``tracks``; serve with ``pop(0)``; refill when empty.
- After a refill, if q[0] is the mock just served from that track, swap q[0] and q[1].

Follow-ups
----------
- Weight tracks (two SWE sessions per GenAI session): repeat a track in ``tracks``.
- Space repeats of a failed mock with Leitner boxes (Chapter 44, ex02).
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "mocks.json"
ROOT = Path(__file__).resolve().parents[3]
TRACK_COUNTS = {"SWE": 4, "Data/ML": 3, "GenAI/LLM": 3}


@dataclass(frozen=True)
class Mock:
    id: str
    track: str
    rubric: str
    minutes: int
    role: str
    title: str
    segments: tuple[tuple[str, int], ...]
    problems: tuple[dict, ...]
    strong: tuple[str, ...]
    followups: tuple[str, ...]


def load_mocks(path: Path = DATA, root: Path = ROOT) -> list[Mock]:
    raise NotImplementedError("TODO")


def by_id(mocks: list[Mock]) -> dict[str, Mock]:
    return {m.id: m for m in mocks}


def timebox(mock: Mock) -> list[tuple[str, int, int]]:
    raise NotImplementedError("TODO")


def rotation(mocks: list[Mock], tracks: list[str], sessions: int, seed: int = 0) -> list[str]:
    raise NotImplementedError("TODO")


def weekly(ids: list[str], per_week: int) -> list[list[str]]:
    raise NotImplementedError("TODO")


def main() -> None:
    mocks = load_mocks()
    print(f"{len(mocks)} mocks:", {t: [m.id for m in mocks if m.track == t] for t in TRACK_COUNTS})
    for m in mocks:
        refs = ", ".join(p["ref"] for p in m.problems)
        print(f"  {m.id} {m.track:<9} {m.minutes:>2} min  {m.title}  [{refs}]")

    print("\nTime boxes for S2:")
    for name, start, end in timebox(by_id(mocks)["S2"]):
        print(f"  {start:>2}-{end:<2} {name}")

    print("\nSWE-track loop, 8 sessions, 2 per week (seed 7):")
    ids = rotation(mocks, ["SWE", "SWE", "Data/ML"], 8, seed=7)
    for w, week in enumerate(weekly(ids, 2), 1):
        minutes = sum(by_id(mocks)[i].minutes for i in week)
        print(f"  week {w}: {week}  ({minutes} min)")

    print("\nAll three tracks, 10 sessions (seed 0):", rotation(mocks, list(TRACK_COUNTS), 10))


if __name__ == "__main__":
    main()
