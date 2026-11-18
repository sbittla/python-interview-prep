"""
Exercise 06 — Decision Tree Classifier (Entropy / Gini)               [Tier: ★ Core]
Chapter 36 · Pattern: greedy recursive partitioning · Target time: 40 min

Problem
-------
Build a CART-style binary classification tree on numeric features.

- ``entropy(y)`` = −Σ p_c log₂ p_c and ``gini(y)`` = 1 − Σ p_c²;
- ``information_gain(y, left_mask, criterion)`` = impurity(parent) − weighted child impurity;
- ``best_split(X, y, criterion)`` → (feature, threshold, gain) or None. Candidate thresholds are
  midpoints between consecutive distinct sorted values; the split is ``x[f] <= threshold``. Ties:
  the first (lowest feature, then lowest threshold) best split wins;
- ``build_tree(X, y, max_depth, min_samples_split, criterion)`` returning nested dicts
  (leaf: {"leaf": True, "value": cls, "counts": [...]}; internal: {"feature", "threshold",
  "left", "right", "gain"});
- ``predict(tree, X)`` and ``tree_to_lines(tree, feature_names)`` for printing.

Examples
--------
>>> round(entropy(np.array([0, 0, 1, 1])), 4), round(gini(np.array([0, 0, 1, 1])), 4)
(1.0, 0.5)

Constraints
-----------
- NumPy only. Integer labels 0..C−1. Stop when depth == max_depth, the node is pure,
  it has fewer than min_samples_split samples, or no split has positive gain.

Approach ladder
---------------
1. Brute force split search — for every feature and every candidate threshold, partition the node
   and recompute both impurities: O(d · n²) per node.
2. Sorted sweep — sort each feature once (O(n log n)), sweep left→right maintaining class-count
   prefix sums; every candidate's impurity is then O(C): O(d · n log n) per node. This is how real
   libraries do it.
3. Histogram / binned splits (LightGBM, XGBoost "hist") — bucket each feature into ≤256 bins:
   O(d · n) per node, used for large data.

Hints
-----
- Prefix counts: one-hot the labels in sorted order and take a cumulative sum.
- Only positions where x_sorted[i] < x_sorted[i+1] are valid split points.
- Information gain with entropy is the same as mutual information between the split and the label.

Follow-ups
----------
- Why do unpruned trees overfit? (Each leaf can isolate one sample.) Remedies: max_depth,
  min_samples_leaf, cost-complexity pruning, or ensembles (Exercise 07).
- Regression trees: replace impurity with variance (MSE) and leaves with the mean.
- Entropy vs Gini rarely changes the tree much; Gini avoids a log and is slightly cheaper.
"""
from __future__ import annotations

import numpy as np


def make_data(n: int = 300, seed: int = 0):
    """Two features in [0, 10]; label 1 iff x0 > 6, or x0 > 2 and x1 > 5 (plus 5% label noise)."""
    rng = np.random.default_rng(seed)
    X = np.round(rng.uniform(0, 10, size=(n, 2)), 2)
    y = ((X[:, 0] > 6) | ((X[:, 0] > 2) & (X[:, 1] > 5))).astype(int)
    flip = rng.random(n) < 0.05
    y[flip] = 1 - y[flip]
    return X, y


def entropy(y: np.ndarray) -> float:
    if len(y) == 0:
        return 0.0
    p = np.bincount(y) / len(y)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum()) + 0.0   # "+ 0.0" turns -0.0 into 0.0


def gini(y: np.ndarray) -> float:
    if len(y) == 0:
        return 0.0
    p = np.bincount(y) / len(y)
    return float(1.0 - (p ** 2).sum())


IMPURITY = {"entropy": entropy, "gini": gini}


def information_gain(y: np.ndarray, left_mask: np.ndarray, criterion: str = "entropy") -> float:
    f = IMPURITY[criterion]
    n, nl = len(y), int(left_mask.sum())
    nr = n - nl
    return f(y) - (nl / n) * f(y[left_mask]) - (nr / n) * f(y[~left_mask])


def best_split_brute(X: np.ndarray, y: np.ndarray, criterion: str = "entropy"):
    best = None
    for f in range(X.shape[1]):
        vals = np.unique(X[:, f])
        for thr in (vals[:-1] + vals[1:]) / 2:
            g = information_gain(y, X[:, f] <= thr, criterion)
            if g > 1e-12 and (best is None or g > best[2] + 1e-12):
                best = (f, float(thr), float(g))
    return best


def _impurity_from_counts(counts: np.ndarray, criterion: str) -> np.ndarray:
    """counts: (m, C) class counts -> (m,) impurity."""
    tot = counts.sum(axis=1, keepdims=True)
    p = counts / np.maximum(tot, 1)
    if criterion == "gini":
        return 1.0 - (p ** 2).sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        logs = np.where(p > 0, np.log2(np.where(p > 0, p, 1.0)), 0.0)
    return -(p * logs).sum(axis=1)


def best_split(X: np.ndarray, y: np.ndarray, criterion: str = "entropy", features=None):
    """Sorted-sweep split search. ``features`` optionally restricts the candidate features."""
    n = len(y)
    n_classes = int(y.max()) + 1
    parent = IMPURITY[criterion](y)
    best = None
    for f in (range(X.shape[1]) if features is None else features):
        order = np.argsort(X[:, f], kind="stable")
        xs, ys = X[order, f], y[order]
        left = np.cumsum(np.eye(n_classes)[ys], axis=0)[:-1]      # counts in first i+1 samples
        right = left[-1] + np.eye(n_classes)[ys[-1]] - left
        valid = xs[:-1] < xs[1:]
        if not valid.any():
            continue
        nl = np.arange(1, n)
        child = (nl * _impurity_from_counts(left, criterion)
                 + (n - nl) * _impurity_from_counts(right, criterion)) / n
        gains = np.where(valid, parent - child, -np.inf)
        i = int(np.argmax(gains))
        g = float(gains[i])
        if g > 1e-12 and (best is None or g > best[2] + 1e-12):
            best = (int(f), float((xs[i] + xs[i + 1]) / 2), g)
    return best


def _leaf(y: np.ndarray, n_classes: int) -> dict:
    counts = np.bincount(y, minlength=n_classes)
    return {"leaf": True, "value": int(counts.argmax()), "counts": counts.tolist()}


def build_tree(X: np.ndarray, y: np.ndarray, max_depth: int = 3, min_samples_split: int = 2,
               criterion: str = "entropy", depth: int = 0, n_classes: int | None = None) -> dict:
    n_classes = n_classes or int(y.max()) + 1
    if depth >= max_depth or len(y) < min_samples_split or len(np.unique(y)) == 1:
        return _leaf(y, n_classes)
    split = best_split(X, y, criterion)
    if split is None:
        return _leaf(y, n_classes)
    f, thr, gain = split
    mask = X[:, f] <= thr
    return {
        "leaf": False, "feature": f, "threshold": thr, "gain": gain,
        "left": build_tree(X[mask], y[mask], max_depth, min_samples_split, criterion, depth + 1, n_classes),
        "right": build_tree(X[~mask], y[~mask], max_depth, min_samples_split, criterion, depth + 1, n_classes),
    }


def predict_one(tree: dict, x: np.ndarray) -> int:
    node = tree
    while not node["leaf"]:
        node = node["left"] if x[node["feature"]] <= node["threshold"] else node["right"]
    return node["value"]


def predict(tree: dict, X: np.ndarray) -> np.ndarray:
    return np.array([predict_one(tree, x) for x in X])


def tree_to_lines(tree: dict, feature_names, indent: str = "") -> list[str]:
    if tree["leaf"]:
        return [f"{indent}predict {tree['value']}  counts={tree['counts']}"]
    name = feature_names[tree["feature"]]
    lines = [f"{indent}if {name} <= {tree['threshold']:.4f}:  (gain={tree['gain']:.4f})"]
    lines += tree_to_lines(tree["left"], feature_names, indent + "    ")
    lines.append(f"{indent}else:  # {name} > {tree['threshold']:.4f}")
    lines += tree_to_lines(tree["right"], feature_names, indent + "    ")
    return lines


def main() -> None:
    print("entropy/gini of [0,0,1,1]:", round(entropy(np.array([0, 0, 1, 1])), 4),
          round(gini(np.array([0, 0, 1, 1])), 4))
    print("entropy/gini of [0,0,0,1]:", round(entropy(np.array([0, 0, 0, 1])), 4),
          round(gini(np.array([0, 0, 0, 1])), 4))
    print("entropy/gini of pure [1,1,1]:", round(entropy(np.array([1, 1, 1])), 4),
          round(gini(np.array([1, 1, 1])), 4))

    X, y = make_data()
    X_tr, y_tr, X_te, y_te = X[:200], y[:200], X[200:], y[200:]
    for crit in ("entropy", "gini"):
        fast, slow = best_split(X_tr, y_tr, crit), best_split_brute(X_tr, y_tr, crit)
        print(f"{crit}: sweep split={fast[0]}, {fast[1]:.4f}, gain={fast[2]:.4f} | "
              f"brute agrees: {fast[0] == slow[0] and np.isclose(fast[1], slow[1])}")

    tree = build_tree(X_tr, y_tr, max_depth=3, criterion="entropy")
    print("learned tree (entropy, max_depth=3):")
    for line in tree_to_lines(tree, ["x0", "x1"]):
        print("  " + line)
    for crit in ("entropy", "gini"):
        for depth in (1, 2, 3, 5, 12):
            t = build_tree(X_tr, y_tr, max_depth=depth, criterion=crit)
            tr = np.mean(predict(t, X_tr) == y_tr)
            te = np.mean(predict(t, X_te) == y_te)
            print(f"  {crit:7s} depth={depth:2d} train acc={tr:.4f} test acc={te:.4f}")


if __name__ == "__main__":
    main()
