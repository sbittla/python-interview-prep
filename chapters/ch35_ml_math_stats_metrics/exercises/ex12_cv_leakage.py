"""
Exercise 12 — Cross-Validation Splits Without Leakage            [Tier: ★ Core]
Chapter 35 · Pattern: fit every step on the training fold only · Target time: 30 min

Problem
-------
Write index splitters that return a list of (train_idx, test_idx) numpy arrays:

1. ``kfold(n, k, shuffle=True, seed=0)``: every index in exactly one test fold; fold sizes
   differ by at most 1 (the first n % k folds get one extra). ValueError unless 2 <= k <= n.
2. ``stratified_kfold(y, k, seed=0)``: same, and each class's count per test fold differs
   by at most 1 across folds (shuffle each class, deal it round-robin).
3. ``group_kfold(groups, k)``: no group appears in both train and test (all rows of one
   patient/user stay together). Greedy: largest group first, into the lightest fold.
4. ``time_series_split(n, k)``: expanding window; test fold j is a contiguous block, train
   is everything strictly before it (no future rows in training).
5. ``class_weights(y)`` = n / (C * count_c): "balanced" weights for imbalance.
6. ``cv_accuracy(X, y, select_inside_folds)``: the leakage demo. Pick the m features most
   correlated with y, then score a nearest-centroid classifier with 5-fold CV. Selecting
   on *all* rows before CV leaks the test labels into the features.

Examples
--------
>>> [len(te) for _, te in kfold(10, 3)]
[4, 3, 3]

Constraints
-----------
- numpy only; deterministic given the seed.

Hints
-----
- kfold: permute indices once, cut into k contiguous chunks of size n//k or n//k + 1.
- stratified: shuffle each class's indices and deal them out round-robin, continuing the
  rotation from class to class so overall fold sizes also stay balanced.
- group: sort groups by size descending; give each to the fold with the fewest rows so far.
- time series: test blocks of size n // (k + 1) at the end of the series; train = all before.
- Leakage demo: the feature selection and the scaler must be fitted on ``X[train]`` only.

Wrong-but-tempting
------------------
- Standardising or selecting features on the full dataset "because it is unsupervised".
- Shuffled k-fold on time series or on several rows per user.
- Oversampling the minority class before splitting: copies land in both train and test.

Follow-ups
----------
- Nested CV: tune hyper-parameters in an inner loop, report the outer loop.
- Oversample (SMOTE, duplication) only the training fold, never before splitting.
- Target leakage vs train/test contamination: a feature computed from the label or the
  future is a leak even with perfect splitting.
- Edge cases: k > n, a class rarer than k, one huge group, n not divisible by k + 1.
"""
from __future__ import annotations

import numpy as np


def kfold(n: int, k: int, shuffle: bool = True, seed: int = 0):
    raise NotImplementedError("TODO")


def stratified_kfold(y, k: int, seed: int = 0):
    raise NotImplementedError("TODO")


def group_kfold(groups, k: int):
    raise NotImplementedError("TODO")


def time_series_split(n: int, k: int):
    raise NotImplementedError("TODO")


def class_weights(y) -> dict:
    raise NotImplementedError("TODO")


def _top_features(X, y, m):
    Xc, yc = X - X.mean(axis=0), y - y.mean()
    corr = np.abs(Xc.T @ yc) / (np.linalg.norm(Xc, axis=0) * np.linalg.norm(yc) + 1e-12)
    return np.argsort(-corr, kind="mergesort")[:m]


def _nearest_centroid(Xtr, ytr, Xte):
    mu0, mu1 = Xtr[ytr == 0].mean(axis=0), Xtr[ytr == 1].mean(axis=0)
    d0, d1 = ((Xte - mu0) ** 2).sum(axis=1), ((Xte - mu1) ** 2).sum(axis=1)
    return (d1 < d0).astype(int)


def cv_accuracy(X, y, select_inside_folds: bool, m: int = 20, k: int = 5, seed: int = 0) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    print("kfold(10, 3) test sizes:", [len(te) for _, te in kfold(10, 3)])
    y = np.array([0] * 12 + [1] * 3)
    print("stratified positives per fold:", [int(y[te].sum()) for _, te in stratified_kfold(y, 3, seed=1)])
    print("plain kfold positives per fold:", [int(y[te].sum()) for _, te in kfold(15, 3, shuffle=False)])
    groups = np.array(list("aaaabbbccdeeeff"))
    for tr, te in group_kfold(groups, 3):
        print("  group fold test groups:", sorted(set(groups[te].tolist())),
              " overlap with train:", sorted(set(groups[te]) & set(groups[tr])))
    for tr, te in time_series_split(10, 3):
        print("  time split train", tr.tolist(), "test", te.tolist())
    print("balanced class weights:", {c: round(w, 3) for c, w in class_weights(y).items()})

    rng = np.random.default_rng(35)
    X = rng.normal(size=(60, 2000))                   # pure noise features
    yr = rng.permutation(np.r_[np.zeros(30, int), np.ones(30, int)])   # labels carry no signal
    print("random labels, select features BEFORE CV:", round(cv_accuracy(X, yr, False), 2))
    print("random labels, select features INSIDE CV:", round(cv_accuracy(X, yr, True), 2), "(chance = 0.5)")


if __name__ == "__main__":
    main()
