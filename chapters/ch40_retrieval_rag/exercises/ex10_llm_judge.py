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

Hints
-----
- swap: call ``compare(ref, b, a)`` and map its "A" back to answer b.
- flip rate is measured with the swap whatever mode is reported.
- kappa: p_e = sum over labels of (count_x / n) * (count_y / n).

Wrong-but-tempting
------------------
- Reporting single-order accuracy only: 0.9 accuracy can hide a 40 % flip rate.
- Believing order swapping fixes length bias.
- Raw agreement instead of kappa when one label dominates.

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
        raise NotImplementedError("TODO")

    @staticmethod
    def quality(reference: str, answer: str) -> float:
        raise NotImplementedError("TODO")

    def compare(self, reference: str, a: str, b: str) -> str:
        raise NotImplementedError("TODO")


def swap_verdict(judge: MockJudge, reference: str, a: str, b: str) -> str:
    raise NotImplementedError("TODO")


def judge_report(judge: MockJudge, pairs: list[dict], swap: bool) -> dict:
    raise NotImplementedError("TODO")


def cohen_kappa(x: list[str], y: list[str]) -> float:
    raise NotImplementedError("TODO")


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
