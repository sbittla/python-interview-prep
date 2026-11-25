"""
Exercise 07 — ROC-AUC Three Ways (with Ties)                     [Tier: ★ Core]
Chapter 35 · Pattern: ranking statistic / Mann-Whitney U · Target time: 25 min

Problem
-------
Given binary labels y (1 = positive) and real scores s (higher = more positive):

1. ``auc_pairs``: brute force. AUC = P(score of a random positive > score of a random
   negative), counting ties as 1/2.
2. ``roc_curve`` -> (fpr, tpr), one point per *distinct* threshold (descending), starting at
   (0, 0); ``auc_trapezoid`` integrates it with the trapezoid rule.
3. ``auc_rank``: Mann-Whitney. With 1-based ranks of all scores (tied scores share their
   average rank), AUC = (R_pos - n_pos (n_pos + 1) / 2) / (n_pos * n_neg), R_pos = sum of
   positive ranks.
All three must agree exactly up to float rounding. Raise ``ValueError`` if either class is
missing (AUC undefined).

Examples
--------
>>> auc_pairs([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8])
0.75
>>> auc_rank([0, 1], [0.5, 0.5])          # a tie is worth half a correct pair
0.5

Constraints
-----------
- n up to 10^6 for the fast rungs.

Hints
-----
- Brute force: loop over (positive, negative) pairs; a tie is worth 0.5.
- ROC: sort by descending score, cumulative TP and FP, but read them only at the *end of each
  tied block* (one point per distinct threshold), then prepend (0, 0).
- Rank formula: tied scores share the average of the ranks they occupy.
- ``np.argsort(..., kind="mergesort")`` is stable, which keeps ties in input order.

Wrong-but-tempting
------------------
- ``argsort().argsort()`` as ranks: ties get distinct ranks, the result depends on order.
- One ROC point per sample: a tied block becomes a staircase, again order dependent.
- Returning 0.5 (or crashing with 0/0) when one class is absent instead of raising.

Follow-ups
----------
- AUC ignores calibration: any strictly increasing transform of s leaves it unchanged.
- Under heavy class imbalance, PR-AUC / average precision is more informative (ex08).
- Wrong but tempting: ranks from ``argsort().argsort()`` (no tie averaging), or one ROC
  point per sample, both make the answer depend on input order when scores tie.
- AUC < 0.5 means the ranking is inverted: flip the score.
- Edge cases: one class only (error), all scores equal (0.5), perfect / inverted ranking.
"""
from __future__ import annotations

import numpy as np


def _prep(y, s):
    y, s = np.asarray(y), np.asarray(s, dtype=float)
    n_pos = int((y == 1).sum())
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        raise ValueError("AUC needs at least one positive and one negative")
    return y, s, n_pos, n_neg


def auc_pairs(y, s) -> float:
    raise NotImplementedError("TODO")


def roc_curve(y, s):
    raise NotImplementedError("TODO")


def auc_trapezoid(y, s) -> float:
    raise NotImplementedError("TODO")


def average_ranks(s) -> np.ndarray:
    raise NotImplementedError("TODO")


def auc_rank(y, s) -> float:
    raise NotImplementedError("TODO")


def auc_rank_no_tie_fix(y, s) -> float:
    """Wrong but tempting: ordinal ranks, so tied scores get different ranks."""
    raise NotImplementedError("TODO")


def main() -> None:
    y = [0, 0, 1, 1]
    s = [0.1, 0.4, 0.35, 0.8]
    print("hand case  :", auc_pairs(y, s), auc_trapezoid(y, s), auc_rank(y, s))
    fpr, tpr = roc_curve(y, s)
    print("ROC points :", list(zip(fpr.tolist(), tpr.tolist())))

    yt = [1, 0, 1, 0, 1, 0]
    st = [0.9, 0.9, 0.5, 0.5, 0.5, 0.1]           # ties across classes
    print("ties       :", round(auc_pairs(yt, st), 6), round(auc_trapezoid(yt, st), 6), round(auc_rank(yt, st), 6))
    print("no tie fix :", round(auc_rank_no_tie_fix(yt, st), 6), "vs reversed input:",
          round(auc_rank_no_tie_fix(yt[::-1], st[::-1]), 6))
    print("all equal  :", auc_rank([0, 1, 0, 1], [3, 3, 3, 3]))

    rng = np.random.default_rng(35)
    yr = (rng.random(2000) < 0.3).astype(int)
    sr = np.round(yr + rng.normal(size=2000), 1)    # rounded -> many ties
    a, b, c = auc_pairs(yr, sr), auc_trapezoid(yr, sr), auc_rank(yr, sr)
    print(f"random n=2000: pairs={a:.6f} trapezoid={b:.6f} rank={c:.6f}  agree: {abs(a - b) < 1e-12 and abs(a - c) < 1e-12}")
    print("monotone transform keeps AUC:", abs(auc_rank(yr, np.exp(3 * sr)) - c) < 1e-12)
    try:
        auc_rank([1, 1], [0.2, 0.3])
    except ValueError as e:
        print("one class  -> ValueError:", e)


if __name__ == "__main__":
    main()
