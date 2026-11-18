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

Follow-ups
----------
- Calibrate: compare self-ratings with actual mock rubric scores and flag over-confidence.
- Turn the weak areas into a two-week repair plan (Section 48.1).
"""
from __future__ import annotations
import json
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / 'data' / 'self_assessment.json'
AREAS = {'python_fluency': [5, 6, 7, 23, 24, 25, 26], 'complexity': [8, 22], 'arrays_hashing': [9, 10, 11], 'linear_structures': [12, 13], 'trees_graphs': [14, 15, 16, 17], 'techniques': [18, 19, 20, 21], 'practical': [29, 30, 31, 32], 'concurrency': [27, 28], 'data_ml': [33, 34, 35, 36, 37], 'genai': [38, 39, 40, 41, 42, 43], 'communication': [2, 46, 47]}
_W = {'S': (3, 3, 4, 3, 4, 3, 3, 2, 0, 0, 3), 'M': (3, 2, 3, 2, 2, 2, 2, 1, 4, 1, 3), 'L': (3, 2, 3, 2, 2, 2, 2, 2, 1, 4, 3)}
WEIGHTS = {t: dict(zip(AREAS, w)) for t, w in _W.items()}

def validate(ratings: dict[str, int]) -> None:
    raise NotImplementedError('TODO')

def self_score(ratings: dict[str, int], track: str) -> float:
    raise NotImplementedError('TODO')

def mock_evidence(scores: list[float]) -> float | None:
    raise NotImplementedError('TODO')

def readiness(ratings: dict[str, int], track: str, mocks: list[float]) -> float:
    raise NotImplementedError('TODO')

def gated(ratings: dict[str, int], track: str) -> list[str]:
    raise NotImplementedError('TODO')

def verdict(score: float, gated: bool) -> str:
    raise NotImplementedError('TODO')

def weak_areas(ratings: dict[str, int], track: str, k: int=3) -> list[tuple[str, int, list[int]]]:
    raise NotImplementedError('TODO')

def report(candidate: dict) -> str:
    raise NotImplementedError('TODO')

def main() -> None:
    data = json.loads(DATA.read_text(encoding='utf-8'))
    for cand in data['candidates']:
        print(report(cand))
        print()
    print('Weights per track (sum):', {t: sum(w.values()) for t, w in sorted(WEIGHTS.items())})
    try:
        self_score({'python_fluency': 5}, 'S')
    except ValueError as exc:
        print('invalid input ->', exc)
if __name__ == '__main__':
    main()
