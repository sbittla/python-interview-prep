"""
Exercise 08 — Average Precision, PR-AUC and Calibration          [Tier: ★ Core]
Chapter 35 · Pattern: threshold sweep + binning · Target time: 25 min

Problem
-------
Binary labels y (1 = positive), scores/probabilities p.

1. ``pr_curve(y, p)`` -> (recall, precision) at each *distinct* threshold, descending.
2. ``average_precision(y, p)``: the step-wise (non-interpolated) definition
       AP = sum_k (R_k - R_{k-1}) * P_k,   R_0 = 0,
   over distinct thresholds k (the definition scikit-learn uses). Tied scores form one step.
3. ``average_precision_brute``: recompute P and R at every distinct threshold t by counting
   p >= t directly. O(n * T).
4. ``pr_auc_trapezoid``: trapezoid over (0, 1) followed by the PR points. Linear
   interpolation between PR points is not achievable by any classifier, so this area can
   over- or understate AP (the hand case below understates it): report AP instead.
5. ``brier(y, p)`` = mean((p - y)^2) and ``ece(y, p, bins=10)``: expected calibration
   error with equal-width bins [0, 0.1), ..., [0.9, 1.0]:
       ECE = sum_b (n_b / n) * |mean(y in b) - mean(p in b)|.

Examples
--------
>>> average_precision([1, 0, 1, 0], [0.9, 0.8, 0.7, 0.1])     # (1/2)*1 + (1/2)*(2/3)
0.8333333333333333

Constraints
-----------
- At least one positive (AP undefined otherwise: ``ValueError``); 0 <= p <= 1 for calibration.

Hints
-----
- Same sort-and-cumsum sweep as the ROC curve in ex07, reading TP at the end of each tied
  block; precision = TP / (number predicted positive), recall = TP / n_pos.
- AP = sum of (recall step) * (precision at that step), starting from recall 0.
- ECE: bin index = min(int(p * bins), bins - 1); ``np.bincount`` with ``weights=`` gives the
  per-bin sums of y and p.

Wrong-but-tempting
------------------
- Trapezoid area under the PR curve called "AP": a different (and not achievable) number.
- Comparing AP across datasets with different positive rates.
- Judging calibration from AUC: a monotone distortion keeps AUC and AP identical.

Follow-ups
----------
- AP's baseline is the positive rate (a random ranking scores ~ prevalence), ROC-AUC's is 0.5:
  at 1 % prevalence AP exposes a weak ranker that ROC-AUC flatters.
- "Mean of precision at each positive's rank" equals step AP only without ties.
- Other AP definitions: 11-point interpolated (old PASCAL VOC), AP@K (ex10). State yours.
- Calibration is orthogonal to ranking: a monotone distortion keeps AUC and AP but ruins ECE.
- ECE depends on the binning; Brier is a proper scoring rule and needs no bins.
- Edge cases: no positives (error), all scores tied, p exactly 1.0 (goes in the last bin).
"""
from __future__ import annotations

import numpy as np


def _prep(y, p):
    y, p = np.asarray(y), np.asarray(p, dtype=float)
    n_pos = int((y == 1).sum())
    if n_pos == 0:
        raise ValueError("average precision needs at least one positive")
    return (y == 1), p, n_pos


def pr_curve(y, p):
    raise NotImplementedError("TODO")


def average_precision(y, p) -> float:
    raise NotImplementedError("TODO")


def average_precision_brute(y, p) -> float:
    raise NotImplementedError("TODO")


def pr_auc_trapezoid(y, p) -> float:
    raise NotImplementedError("TODO")


def brier(y, p) -> float:
    raise NotImplementedError("TODO")


def ece(y, p, bins: int = 10) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    y, p = [1, 0, 1, 0], [0.9, 0.8, 0.7, 0.1]
    print("hand case AP:", round(average_precision(y, p), 6), " brute:", round(average_precision_brute(y, p), 6),
          " trapezoid:", round(pr_auc_trapezoid(y, p), 6))
    yt, pt = [1, 0, 1, 1, 0], [0.8, 0.8, 0.5, 0.3, 0.3]
    print("ties AP     :", round(average_precision(yt, pt), 6), " brute:", round(average_precision_brute(yt, pt), 6))

    rng = np.random.default_rng(35)
    n = 20_000
    y_rare = (rng.random(n) < 0.01).astype(int)
    score = y_rare * 1.5 + rng.normal(size=n)         # a mediocre ranker at 1 % prevalence
    order = np.argsort(score)                         # ROC-AUC by rank statistic (ex07), inline
    ranks = np.empty(n)
    ranks[order] = np.arange(1, n + 1)                # continuous scores: no ties
    n_pos = y_rare.sum()
    roc_auc = (ranks[y_rare == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * (n - n_pos))
    print(f"1% prevalence: ROC-AUC={roc_auc:.3f}  AP={average_precision(y_rare, score):.3f}  "
          f"random-ranker AP ~ {y_rare.mean():.3f}")

    q = rng.uniform(0.02, 0.98, size=n)               # true probabilities
    yc = (rng.random(n) < q).astype(int)
    logit = np.log(q / (1 - q))
    over = 1 / (1 + np.exp(-3 * logit))               # same ranking, overconfident
    print(f"calibrated   : ECE={ece(yc, q):.3f}  Brier={brier(yc, q):.3f}  AP={average_precision(yc, q):.4f}")
    print(f"overconfident: ECE={ece(yc, over):.3f}  Brier={brier(yc, over):.3f}  AP={average_precision(yc, over):.4f}")
    print("ECE hand case:", round(ece([0, 1, 1, 1], [0.05, 0.95, 0.95, 1.0]), 4))


if __name__ == "__main__":
    main()
