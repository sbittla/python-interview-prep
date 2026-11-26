"""
Exercise 10 — LLM-as-Judge Pitfalls: Position Bias, Length Bias, Agreement   [Tier: ★ Core]
Chapter 40 · Pattern: evaluate the evaluator · Target time: 30 min

Problem
-------
``MockJudge(position_bias=0.0, length_bias=0.0)`` is a deterministic pairwise judge:
``compare(reference, a, b)`` returns ``"A"`` or ``"B"``. Its true signal is
``quality(reference, answer)`` = fraction of the reference's distinct content terms found in the
answer. It then adds ``length_bias`` × (answer words) to both sides and ``position_bias`` to
whichever answer is shown first, and picks A when the totals tie (one more position bias).
These are the two biases most often reported for real LLM judges.

1. ``swap_verdict(judge, reference, a, b)``: judge (a, b) and (b, a); return ``"A"``/``"B"`` if
   both orders agree on the same *answer*, else ``"inconsistent"``.
2. ``judge_report(judge, pairs, swap)``: over ``data/judge_pairs.json`` items
   (``reference, a, b, gold``) return ``{"accuracy", "coverage", "flip_rate"}``: accuracy over
   the decided items, coverage = decided / all, flip_rate = items whose verdict changes when
   the order is swapped / all (computed whatever ``swap`` is). Rounded to 4.
3. ``cohen_kappa(x, y)``: chance-corrected agreement of two label lists,
   (p_o - p_e) / (1 - p_e), with p_e from each rater's label frequencies; 1.0 if p_e == 1.

Examples
--------
>>> cohen_kappa(["A", "A", "B", "B"], ["A", "B", "B", "B"])
0.5

Approach ladder
---------------
1. Brute force — one judge call per pair, trust the verdict: O(n) calls; position and length
   bias go straight into your metric.
2. Improved   — judge both orders, count disagreements as "inconsistent" (abstain): 2n calls;
   removes pure position effects and *measures* the flip rate.
3. Optimal    — also: a reference answer and a rubric in the judge prompt, length-matched or
   length-controlled comparisons, and agreement (kappa) with a human-labelled sample before
   trusting the judge at scale.
   Why move up: an evaluator you have not validated is a second untested model.

Follow-ups
----------
- Self-preference: a judge may favour outputs from its own model family; use a different model
  or validate against humans.
- Pointwise scores (1–10) drift and cluster; pairwise or binary rubric questions are steadier.
- Judges are LLM calls: cache them (key = judge prompt + model + version) and budget them.
"""
from __future__ import annotations

import json
from collections import Counter

from ragkit import DATA, content_terms


class MockJudge:
    def __init__(self, position_bias: float = 0.0, length_bias: float = 0.0) -> None:
        self.position_bias = position_bias
        self.length_bias = length_bias
        self.calls = 0

    @staticmethod
    def quality(reference: str, answer: str) -> float:
        ref = set(content_terms(reference))
        return len(ref & set(content_terms(answer))) / len(ref) if ref else 0.0

    def compare(self, reference: str, a: str, b: str) -> str:
        self.calls += 1
        sa = self.quality(reference, a) + self.length_bias * len(a.split()) + self.position_bias
        sb = self.quality(reference, b) + self.length_bias * len(b.split())
        return "A" if round(sa, 9) >= round(sb, 9) else "B"


def swap_verdict(judge: MockJudge, reference: str, a: str, b: str) -> str:
    first = judge.compare(reference, a, b)
    second = judge.compare(reference, b, a)
    second_mapped = {"A": "B", "B": "A"}[second]          # "A" in the swapped call means answer b
    return first if first == second_mapped else "inconsistent"


def judge_report(judge: MockJudge, pairs: list[dict], swap: bool) -> dict:
    correct = decided = flips = 0
    for p in pairs:
        single = judge.compare(p["reference"], p["a"], p["b"])
        both = swap_verdict(judge, p["reference"], p["a"], p["b"])
        flips += both == "inconsistent"
        verdict = both if swap else single
        if verdict != "inconsistent":
            decided += 1
            correct += verdict == p["gold"]
    n = len(pairs)
    return {"accuracy": round(correct / decided, 4) if decided else 0.0,
            "coverage": round(decided / n, 4) if n else 0.0,
            "flip_rate": round(flips / n, 4) if n else 0.0}


def cohen_kappa(x: list[str], y: list[str]) -> float:
    if len(x) != len(y) or not x:
        raise ValueError("need two non-empty label lists of equal length")
    n = len(x)
    p_o = sum(a == b for a, b in zip(x, y)) / n
    cx, cy = Counter(x), Counter(y)
    p_e = sum(cx[label] * cy[label] for label in cx) / (n * n)
    return 1.0 if p_e == 1 else round((p_o - p_e) / (1 - p_e), 4)


def load_pairs() -> list[dict]:
    return json.loads((DATA / "judge_pairs.json").read_text(encoding="utf-8"))


def main() -> None:
    print("kappa:", cohen_kappa(["A", "A", "B", "B"], ["A", "B", "B", "B"]),
          cohen_kappa(["A"] * 9 + ["B"], ["A"] * 10))
    pairs = load_pairs()
    judges = {"unbiased": MockJudge(), "position 0.3": MockJudge(position_bias=0.3),
              "length 0.02/word": MockJudge(length_bias=0.02)}
    print(f"\n{'judge':<18}{'mode':<8}{'accuracy':>9}{'coverage':>9}{'flip rate':>10}")
    for name, judge in judges.items():
        for swap in (False, True):
            r = judge_report(judge, pairs, swap)
            print(f"{name:<18}{'swap' if swap else 'single':<8}{r['accuracy']:>9.4f}"
                  f"{r['coverage']:>9.4f}{r['flip_rate']:>10.4f}")

    lj = judges["length 0.02/word"]
    wins = [(i, p["gold"], lj.compare(p["reference"], p["a"], p["b"])) for i, p in enumerate(pairs)
            if lj.compare(p["reference"], p["a"], p["b"]) != p["gold"]]
    print("\nlength-biased judge errors (index, gold, verdict):", wins)
    gold = [p["gold"] for p in pairs]
    for name, judge in judges.items():
        print(f"kappa vs gold, {name:<17}:",
              cohen_kappa([judge.compare(p["reference"], p["a"], p["b"]) for p in pairs], gold))


if __name__ == "__main__":
    main()
