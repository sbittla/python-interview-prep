"""
Exercise 07 — Random Forest: Bootstrap + Feature Subsampling          [Tier: ◆ Extended]
Chapter 36 · Pattern: bagging ensemble · Target time: 35 min

Problem
-------
Build a random-forest classifier on top of a Gini decision tree.

- ``bootstrap_indices(n, rng)`` — n indices sampled with replacement;
- ``fit_tree(X, y, max_depth, max_features, rng)`` — a Gini tree where, at every node, only a
  random subset of ``max_features`` features (without replacement) is considered;
- ``fit_forest(X, y, n_trees, max_depth, max_features, seed)`` → list of (tree, oob_mask);
- ``predict_forest(forest, X)`` — majority vote (ties → smallest label);
- ``oob_accuracy(forest, X, y)`` — each sample is scored only by trees whose bootstrap did not
  contain it.

Examples
--------
>>> rng = np.random.default_rng(0)
>>> len(bootstrap_indices(5, rng))
5

Constraints
-----------
- NumPy only; every random choice comes from one ``np.random.default_rng(seed)``.

Approach ladder
---------------
1. Single deep tree — low bias, very high variance: it memorises label noise.
2. Bagging — average B trees trained on bootstrap resamples: the variance of an average of B
   identically distributed predictors with pairwise correlation ρ is ρσ² + (1−ρ)σ²/B.
3. Random forest — also subsample features at each split (typically √d) to lower ρ, which bagging
   alone cannot reduce. Cost: O(B · d_sub · n log n · depth) to train, trivially parallel.

Hints
-----
- A bootstrap sample of size n contains on average 1 − (1 − 1/n)ⁿ ≈ 63.2% distinct points;
  the remaining ≈36.8% are "out of bag" and give a free validation estimate.
- Reuse the sorted-sweep Gini split from Exercise 06 restricted to the sampled features.

Follow-ups
----------
- Random forest vs gradient boosting: bagging reduces variance of low-bias learners; boosting
  reduces bias by fitting residuals sequentially with shallow trees.
- Feature importance: total impurity decrease per feature, or permutation importance.
"""
from __future__ import annotations

import numpy as np


def make_data(n: int = 600, seed: int = 0):
    """5 features; label depends on a circle in (x0, x1) and on x2; x3, x4 are noise; 10% flips."""
    rng = np.random.default_rng(seed)
    X = rng.uniform(-1, 1, size=(n, 5))
    y = (((X[:, 0] ** 2 + X[:, 1] ** 2) < 0.5) ^ (X[:, 2] > 0.5)).astype(int)
    flip = rng.random(n) < 0.10
    y[flip] = 1 - y[flip]
    return X, y


def _gini_counts(counts: np.ndarray) -> np.ndarray:
    tot = counts.sum(axis=1, keepdims=True)
    p = counts / np.maximum(tot, 1)
    return 1.0 - (p ** 2).sum(axis=1)


def _best_split(X, y, features, n_classes):
    n = len(y)
    best = None
    onehot = np.eye(n_classes)
    parent = _gini_counts(np.bincount(y, minlength=n_classes)[None, :].astype(float))[0]
    for f in features:
        order = np.argsort(X[:, f], kind="stable")
        xs, ys = X[order, f], y[order]
        left = np.cumsum(onehot[ys], axis=0)[:-1]
        right = left[-1] + onehot[ys[-1]] - left
        valid = xs[:-1] < xs[1:]
        if not valid.any():
            continue
        nl = np.arange(1, n)
        child = (nl * _gini_counts(left) + (n - nl) * _gini_counts(right)) / n
        gains = np.where(valid, parent - child, -np.inf)
        i = int(np.argmax(gains))
        if gains[i] > 1e-12 and (best is None or gains[i] > best[2] + 1e-12):
            best = (int(f), float((xs[i] + xs[i + 1]) / 2), float(gains[i]))
    return best


def bootstrap_indices(n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.integers(0, n, size=n)


def fit_tree(X, y, max_depth, max_features, rng, depth=0, n_classes=2):
    counts = np.bincount(y, minlength=n_classes)
    if depth >= max_depth or len(y) < 2 or counts.max() == len(y):
        return {"leaf": True, "value": int(counts.argmax())}
    feats = np.sort(rng.choice(X.shape[1], size=max_features, replace=False))
    split = _best_split(X, y, feats, n_classes)
    if split is None:
        return {"leaf": True, "value": int(counts.argmax())}
    f, thr, _ = split
    m = X[:, f] <= thr
    return {"leaf": False, "feature": f, "threshold": thr,
            "left": fit_tree(X[m], y[m], max_depth, max_features, rng, depth + 1, n_classes),
            "right": fit_tree(X[~m], y[~m], max_depth, max_features, rng, depth + 1, n_classes)}


def predict_tree(tree, X):
    out = np.empty(len(X), dtype=int)
    for i, x in enumerate(X):
        node = tree
        while not node["leaf"]:
            node = node["left"] if x[node["feature"]] <= node["threshold"] else node["right"]
        out[i] = node["value"]
    return out


def fit_forest(X, y, n_trees=25, max_depth=8, max_features=2, seed=0):
    rng = np.random.default_rng(seed)
    forest = []
    for _ in range(n_trees):
        idx = bootstrap_indices(len(y), rng)
        oob = np.ones(len(y), dtype=bool)
        oob[idx] = False
        forest.append((fit_tree(X[idx], y[idx], max_depth, max_features, rng), oob))
    return forest


def predict_forest(forest, X):
    votes = np.stack([predict_tree(t, X) for t, _ in forest])      # (B, n)
    ones = votes.sum(axis=0)
    return (ones * 2 > len(forest)).astype(int)                    # tie -> 0 (smaller label)


def oob_accuracy(forest, X, y):
    ones = np.zeros(len(y))
    n_votes = np.zeros(len(y))
    for tree, oob in forest:
        if oob.any():
            ones[oob] += predict_tree(tree, X[oob])
            n_votes[oob] += 1
    scored = n_votes > 0
    pred = (ones[scored] * 2 > n_votes[scored]).astype(int)
    return float(np.mean(pred == y[scored]))


def main() -> None:
    rng = np.random.default_rng(0)
    fractions = [len(np.unique(bootstrap_indices(1000, rng))) / 1000 for _ in range(20)]
    print(f"mean distinct fraction in a bootstrap: {np.mean(fractions):.4f} "
          f"(theory 1-1/e = {1 - np.exp(-1):.4f})")

    X, y = make_data()
    X_tr, y_tr, X_te, y_te = X[:400], y[:400], X[400:], y[400:]

    single = fit_tree(X_tr, y_tr, max_depth=12, max_features=5, rng=np.random.default_rng(0))
    print(f"single deep tree: train acc={np.mean(predict_tree(single, X_tr) == y_tr):.4f} "
          f"test acc={np.mean(predict_tree(single, X_te) == y_te):.4f}")

    bag = fit_forest(X_tr, y_tr, n_trees=25, max_depth=12, max_features=5, seed=0)
    print(f"bagging (25 trees, all 5 features): test acc={np.mean(predict_forest(bag, X_te) == y_te):.4f} "
          f"oob acc={oob_accuracy(bag, X_tr, y_tr):.4f}")

    for B in (1, 5, 25, 75):
        rf = fit_forest(X_tr, y_tr, n_trees=B, max_depth=12, max_features=2, seed=0)
        print(f"random forest B={B:2d} max_features=2: test acc={np.mean(predict_forest(rf, X_te) == y_te):.4f} "
              f"oob acc={oob_accuracy(rf, X_tr, y_tr):.4f}")


if __name__ == "__main__":
    main()
