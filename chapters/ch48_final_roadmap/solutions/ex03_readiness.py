"""
Exercise 03 — Readiness Self-Assessment Scorer                 [Tier: ★ Core]
Chapter 48 · Pattern: weighted scoring + rule-based gating · Target time: 30 min

Problem
-------
Before booking (or confirming) an interview date, rate yourself 0–4 in eleven skill areas:

    0 = never studied   1 = recognise it   2 = can solve with hints
    3 = can solve alone in time   4 = can solve, explain trade-offs and teach it

Each track weights the areas differently (``WEIGHTS``). Compute:

1. the weighted self-assessment score (0–100);
2. the mock-evidence score: the mean of your last two rubric-scored mocks (Chapter 47), or
   ``None`` when you have no mocks yet;
3. the readiness score = 70% self-assessment + 30% mock evidence (self-assessment alone, capped
   at 70, when there is no mock evidence — you cannot be "ready" without a mock);
4. a verdict: ``READY`` (>= 80), ``ALMOST`` (65–79) or ``NOT YET`` (< 65). A *gate* also applies:
   any area with weight >= 3 rated <= 1 caps the verdict at ``ALMOST``;
5. the weakest weighted areas, each mapped to the chapters that repair it.

Examples
--------
>>> round(self_score({a: 4 for a in AREAS}, "S"), 1)
100.0
>>> verdict(85.0, gated=True)
'ALMOST'

Constraints
-----------
- Every area must be present with an integer 0–4, otherwise ``ValueError``.
- Mock scores are 0–100.

Hints
-----
- Normalise: ``sum(w * r / 4) / sum(w) * 100``.
- Rank weak areas by "points lost" = ``w * (4 - r)``, ties by name, skip zero-loss areas.
- Keep verdict logic in its own small function so it is easy to test.

Approach ladder
---------------
1. Brute force — unweighted average of ratings: treats GenAI and graphs as equally important
   for every track, which is wrong.
2. Improved   — per-track weights.
3. Optimal    — weights + objective mock evidence + a gate for critical gaps; O(A) for A areas.

Follow-ups
----------
- Calibrate: compare self-ratings with actual mock rubric scores and flag over-confidence.
- Turn the weak areas into a two-week repair plan (Section 48.1).
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "self_assessment.json"

AREAS = {
    "python_fluency": [5, 6, 7, 23, 24, 25, 26],
    "complexity": [8, 22],
    "arrays_hashing": [9, 10, 11],
    "linear_structures": [12, 13],
    "trees_graphs": [14, 15, 16, 17],
    "techniques": [18, 19, 20, 21],
    "practical": [29, 30, 31, 32],
    "concurrency": [27, 28],
    "data_ml": [33, 34, 35, 36, 37],
    "genai": [38, 39, 40, 41, 42, 43],
    "communication": [2, 46, 47],
}
#                      py cx ah ls tg te pr cc ml ai co
_W = {"S": (3, 3, 4, 3, 4, 3, 3, 2, 0, 0, 3),
      "M": (3, 2, 3, 2, 2, 2, 2, 1, 4, 1, 3),
      "L": (3, 2, 3, 2, 2, 2, 2, 2, 1, 4, 3)}
WEIGHTS = {t: dict(zip(AREAS, w)) for t, w in _W.items()}


def validate(ratings: dict[str, int]) -> None:
    missing = sorted(set(AREAS) - set(ratings))
    if missing:
        raise ValueError(f"missing ratings: {', '.join(missing)}")
    for area, r in ratings.items():
        if area not in AREAS:
            raise ValueError(f"unknown area {area!r}")
        if not isinstance(r, int) or not 0 <= r <= 4:
            raise ValueError(f"{area}: rating must be an int 0-4, got {r!r}")


def self_score(ratings: dict[str, int], track: str) -> float:
    validate(ratings)
    w = WEIGHTS[track]
    return sum(w[a] * ratings[a] / 4 for a in AREAS) / sum(w.values()) * 100


def mock_evidence(scores: list[float]) -> float | None:
    if not scores:
        return None
    last = scores[-2:]
    return sum(last) / len(last)


def readiness(ratings: dict[str, int], track: str, mocks: list[float]) -> float:
    s = self_score(ratings, track)
    m = mock_evidence(mocks)
    if m is None:
        return min(s, 70.0)
    return 0.7 * s + 0.3 * m


def gated(ratings: dict[str, int], track: str) -> list[str]:
    w = WEIGHTS[track]
    return sorted(a for a in AREAS if w[a] >= 3 and ratings[a] <= 1)


def verdict(score: float, gated: bool) -> str:
    if score >= 80:
        v = "READY"
    elif score >= 65:
        v = "ALMOST"
    else:
        v = "NOT YET"
    if gated and v == "READY":
        v = "ALMOST"
    return v


def weak_areas(ratings: dict[str, int], track: str, k: int = 3) -> list[tuple[str, int, list[int]]]:
    w = WEIGHTS[track]
    lost = [(w[a] * (4 - ratings[a]), a) for a in AREAS if w[a] * (4 - ratings[a]) > 0]
    lost.sort(key=lambda t: (-t[0], t[1]))
    return [(a, pts, AREAS[a]) for pts, a in lost[:k]]


def report(candidate: dict) -> str:
    r, t, mocks = candidate["ratings"], candidate["track"], candidate["mock_scores"]
    s, m = self_score(r, t), mock_evidence(mocks)
    total = readiness(r, t, mocks)
    gates = gated(r, t)
    lines = [f"== {candidate['name']} | track {t}"]
    for a in AREAS:
        if WEIGHTS[t][a] == 0:
            continue
        lines.append(f"  {a:<18} w={WEIGHTS[t][a]}  {'#' * r[a]:<4} {r[a]}/4")
    lines.append(f"  self-assessment : {s:5.1f}")
    lines.append(f"  mock evidence   : {'none (score capped at 70)' if m is None else f'{m:5.1f}'}")
    lines.append(f"  readiness       : {total:5.1f} -> {verdict(total, bool(gates))}")
    if gates:
        lines.append(f"  gate            : critical gap in {', '.join(gates)}")
    for a, pts, chs in weak_areas(r, t):
        lines.append(f"  repair {a:<18} (-{pts} pts) chapters {chs}")
    return "\n".join(lines)


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for cand in data["candidates"]:
        print(report(cand))
        print()
    print("Weights per track (sum):", {t: sum(w.values()) for t, w in sorted(WEIGHTS.items())})
    try:
        self_score({"python_fluency": 5}, "S")
    except ValueError as exc:
        print("invalid input ->", exc)


if __name__ == "__main__":
    main()
