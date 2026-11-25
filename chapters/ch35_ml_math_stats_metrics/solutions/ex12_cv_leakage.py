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

Approach ladder
---------------
1. Brute force — a single random train/test split: O(n), but one noisy estimate and
   no guarantee every row is tested.
2. Improved   — k-fold: every row tested once, k fits, O(n) to build the splits. Plain
   k-fold still breaks on imbalance (a fold with no positives), groups and time order.
3. Optimal    — the splitter that matches the data's dependence structure (stratified /
   group / time series), with *every* fitted step (scaling, imputation, feature selection,
   target encoding, oversampling) inside the loop. O(n log n) for the group sort.

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
    if not 2 <= k <= n:
        raise ValueError("need 2 <= k <= n")
    idx = np.random.default_rng(seed).permutation(n) if shuffle else np.arange(n)
    sizes = np.full(k, n // k)
    sizes[: n % k] += 1
    bounds = np.r_[0, np.cumsum(sizes)]
    folds = [idx[bounds[j]:bounds[j + 1]] for j in range(k)]
    return [(np.sort(np.concatenate(folds[:j] + folds[j + 1:])), np.sort(folds[j])) for j in range(k)]


def stratified_kfold(y, k: int, seed: int = 0):
    y = np.asarray(y)
    if not 2 <= k <= len(y):
        raise ValueError("need 2 <= k <= n")
    rng = np.random.default_rng(seed)
    fold_of = np.empty(len(y), dtype=int)
    offset = 0
    for c in np.unique(y):
        members = rng.permutation(np.flatnonzero(y == c))
        fold_of[members] = (np.arange(len(members)) + offset) % k   # deal round-robin
        offset += len(members)                                      # rotate start: balance sizes
    return [(np.flatnonzero(fold_of != j), np.flatnonzero(fold_of == j)) for j in range(k)]


def group_kfold(groups, k: int):
    groups = np.asarray(groups)
    names, counts = np.unique(groups, return_counts=True)
    if k > len(names):
        raise ValueError("need at least k distinct groups")
    load = np.zeros(k, dtype=int)
    fold_of_group = {}
    for g_i in np.argsort(-counts, kind="mergesort"):               # biggest group first
        j = int(np.argmin(load))
        fold_of_group[names[g_i]] = j
        load[j] += counts[g_i]
    fold_of = np.array([fold_of_group[g] for g in groups])
    return [(np.flatnonzero(fold_of != j), np.flatnonzero(fold_of == j)) for j in range(k)]


def time_series_split(n: int, k: int):
    size = n // (k + 1)
    if size == 0:
        raise ValueError("n too small for k folds")
    out = []
    for j in range(k):
        start = n - (k - j) * size                                  # last fold ends at n
        out.append((np.arange(0, start), np.arange(start, start + size)))
    return out


def class_weights(y) -> dict:
    classes, counts = np.unique(y, return_counts=True)
    return {c.item(): float(len(y) / (len(classes) * cnt)) for c, cnt in zip(classes, counts)}


def _top_features(X, y, m):
    Xc, yc = X - X.mean(axis=0), y - y.mean()
    corr = np.abs(Xc.T @ yc) / (np.linalg.norm(Xc, axis=0) * np.linalg.norm(yc) + 1e-12)
    return np.argsort(-corr, kind="mergesort")[:m]


def _nearest_centroid(Xtr, ytr, Xte):
    mu0, mu1 = Xtr[ytr == 0].mean(axis=0), Xtr[ytr == 1].mean(axis=0)
    d0, d1 = ((Xte - mu0) ** 2).sum(axis=1), ((Xte - mu1) ** 2).sum(axis=1)
    return (d1 < d0).astype(int)


def cv_accuracy(X, y, select_inside_folds: bool, m: int = 20, k: int = 5, seed: int = 0) -> float:
    leaked = None if select_inside_folds else _top_features(X, y, m)   # sees every label
    accs = []
    for tr, te in stratified_kfold(y, k, seed):
        feats = _top_features(X[tr], y[tr], m) if select_inside_folds else leaked
        mu, sd = X[tr][:, feats].mean(axis=0), X[tr][:, feats].std(axis=0) + 1e-12  # fit on train only
        pred = _nearest_centroid((X[tr][:, feats] - mu) / sd, y[tr], (X[te][:, feats] - mu) / sd)
        accs.append(np.mean(pred == y[te]))
    return float(np.mean(accs))


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
