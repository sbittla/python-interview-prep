"""
Exercise 05 — Interview Signal Scorer                             [Tier: ★ Core]
Chapter 01 · Pattern: weighted average + veto rules · Target time: 25 min

Problem
-------
A common rubric shape rates a handful of signals on a small scale; here 1-4 (1 = strong no,
4 = strong yes). Different rounds weight the signals differently (WEIGHTS; the numbers are
illustrative, not any company's real rubric). Write
`score_round(round_type, ratings)` returning a dict with:

- "score": weighted average rounded to 2 decimals (only signals in WEIGHTS[round_type]);
- "decision": "strong hire" (score >= 3.5), "hire" (>= 2.8), "lean no" (>= 2.2), else "no hire";
  BUT any rating of 1 on a signal whose weight is >= 0.25 forces "no hire" (a veto);
- "weakest": the signal with the lowest rating (ties -> the one with the larger weight, then
  alphabetical) — this is what you should practise next.

Missing ratings raise ValueError naming the missing signals. Ratings outside 1..4 raise ValueError.

Examples
--------
>>> score_round("coding", {"problem_solving": 4, "coding": 4, "communication": 3, "testing": 3})["decision"]
'strong hire'

Constraints
-----------
- Weights of each round type sum to 1.0.


Hints
-----
- sum(WEIGHTS[r][s] * ratings[s] for s in WEIGHTS[r]).
- min(signals, key=lambda s: (ratings[s], -weight[s], s)).

Follow-ups
----------
- Why might a real rubric refuse to average at all and use the lowest signal instead?
"""
from __future__ import annotations

WEIGHTS = {
    "coding": {"problem_solving": 0.35, "coding": 0.30, "communication": 0.15, "testing": 0.20},
    "practical": {"problem_solving": 0.20, "coding": 0.30, "communication": 0.20, "testing": 0.30},
    "ml_coding": {"problem_solving": 0.25, "coding": 0.25, "communication": 0.15,
                  "testing": 0.10, "domain": 0.25},
}

THRESHOLDS = [(3.5, "strong hire"), (2.8, "hire"), (2.2, "lean no")]


def score_round(round_type: str, ratings: dict[str, int]) -> dict:
    """Weighted score, decision and weakest signal for one round."""
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [
        ("coding", {"problem_solving": 4, "coding": 4, "communication": 3, "testing": 3}),
        ("coding", {"problem_solving": 3, "coding": 3, "communication": 2, "testing": 2}),
        ("coding", {"problem_solving": 4, "coding": 1, "communication": 4, "testing": 4}),
        ("practical", {"problem_solving": 3, "coding": 3, "communication": 4, "testing": 2}),
        ("ml_coding", {"problem_solving": 3, "coding": 3, "communication": 3, "testing": 2,
                       "domain": 2}),
    ]
    for rtype, ratings in cases:
        r = score_round(rtype, ratings)
        print(f"{rtype:<10} {ratings} -> {r}")
    try:
        score_round("coding", {"coding": 3})
    except ValueError as exc:
        print("Error:", exc)


if __name__ == "__main__":
    main()
