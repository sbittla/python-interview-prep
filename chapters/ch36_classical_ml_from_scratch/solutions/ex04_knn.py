"""
Exercise 04 — k-Nearest Neighbours Classifier                         [Tier: ★ Core]
Chapter 36 · Pattern: vectorised pairwise distances + voting · Target time: 20 min

Problem
-------
Implement a kNN classifier.

- ``pairwise_sq_dists(A, B)`` — matrix D with D[i, j] = ‖A[i] − B[j]‖², vectorised;
- ``knn_predict(X_train, y_train, X_query, k)`` — majority vote among the k nearest training
  points; ties in the vote go to the smallest label; ties in distance go to the lower training index;
- ``choose_k(X_tr, y_tr, X_val, y_val, ks)`` — return (best_k, {k: accuracy}).

Examples
--------
>>> X = np.array([[0.0], [1.0], [10.0]]); y = np.array([0, 0, 1])
>>> knn_predict(X, y, np.array([[0.4], [9.0]]), k=1).tolist()
[0, 1]

Constraints
-----------
- NumPy only. 1 ≤ k ≤ n_train. Labels are non-negative integers.

Approach ladder
---------------
1. Brute force — Python double loop over (query, train) pairs then sort: O(q·n·d + q·n log n).
2. Vectorised — ‖a−b‖² = ‖a‖² + ‖b‖² − 2a·b gives all distances with one matrix multiply;
   np.argpartition finds the k smallest in O(n) per query instead of O(n log n).
3. At scale — KD-trees / ball trees for low d, approximate nearest neighbours (HNSW, IVF) for
   high d (Chapter 40). kNN has no training cost but O(n·d) memory and query time.

Hints
-----
- Clip tiny negative distances (floating-point cancellation) to 0.
- np.bincount(labels, minlength=c).argmax() returns the smallest label among ties.
- Use a stable sort so that equal distances resolve by index.

Follow-ups
----------
- Why must features be scaled? (Distance is dominated by the largest-scale feature.)
- Weighted kNN: weight votes by 1/distance.
- kNN regression: average the neighbours' targets.
"""
from __future__ import annotations

import numpy as np


def make_data(n: int = 300, seed: int = 0):
    """Two interleaving noisy 'moons' (non-linear boundary)."""
    rng = np.random.default_rng(seed)
    t = rng.uniform(0, np.pi, size=n)
    lab = rng.integers(0, 2, size=n)
    x = np.where(lab == 0, np.cos(t), 1 - np.cos(t))
    yy = np.where(lab == 0, np.sin(t), 0.5 - np.sin(t))
    X = np.c_[x, yy] + rng.normal(scale=0.3, size=(n, 2))
    return X, lab


def pairwise_sq_dists_loops(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    D = np.zeros((len(A), len(B)))
    for i in range(len(A)):
        for j in range(len(B)):
            diff = A[i] - B[j]
            D[i, j] = float(diff @ diff)
    return D


def pairwise_sq_dists(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    a2 = np.sum(A * A, axis=1)[:, None]
    b2 = np.sum(B * B, axis=1)[None, :]
    return np.maximum(a2 + b2 - 2.0 * A @ B.T, 0.0)


def knn_predict(X_train: np.ndarray, y_train: np.ndarray, X_query: np.ndarray, k: int) -> np.ndarray:
    D = pairwise_sq_dists(X_query, X_train)
    nn = np.argsort(D, axis=1, kind="stable")[:, :k]      # (q, k) indices
    n_classes = int(y_train.max()) + 1
    votes = y_train[nn]
    return np.array([np.bincount(v, minlength=n_classes).argmax() for v in votes])


def choose_k(X_tr, y_tr, X_val, y_val, ks):
    scores = {k: float(np.mean(knn_predict(X_tr, y_tr, X_val, k) == y_val)) for k in ks}
    best = max(ks, key=lambda k: (scores[k], -k))          # best accuracy, then smallest k
    return best, scores


def main() -> None:
    X = np.array([[0.0], [1.0], [10.0]])
    y = np.array([0, 0, 1])
    print("toy predictions:", knn_predict(X, y, np.array([[0.4], [9.0]]), k=1).tolist())
    print("vote tie (k=2 -> labels 0 and 1) goes to smaller label:",
          knn_predict(np.array([[0.0], [2.0]]), np.array([1, 0]), np.array([[1.0]]), k=2).tolist())

    X, y = make_data()
    X_tr, y_tr = X[:200], y[:200]
    X_val, y_val = X[200:250], y[200:250]
    X_te, y_te = X[250:], y[250:]

    same = np.allclose(pairwise_sq_dists(X_val[:5], X_tr[:7]), pairwise_sq_dists_loops(X_val[:5], X_tr[:7]))
    print("vectorised distances match loops:", bool(same))

    best, scores = choose_k(X_tr, y_tr, X_val, y_val, ks=[1, 3, 5, 9, 15, 31, 101])
    for k, s in scores.items():
        print(f"  k={k:3d} val acc={s:.4f}")
    print("chosen k:", best)
    print(f"test acc with k={best}: {np.mean(knn_predict(X_tr, y_tr, X_te, best) == y_te):.4f}")

    # Feature scaling matters: blow up an irrelevant noise feature.
    rng = np.random.default_rng(7)
    noise = rng.normal(scale=1000.0, size=(len(X), 1))
    Xn = np.hstack([X, noise])
    acc_raw = np.mean(knn_predict(Xn[:200], y_tr, Xn[250:], best) == y_te)
    mu, sd = Xn[:200].mean(0), Xn[:200].std(0)
    Xs = (Xn - mu) / sd
    acc_std = np.mean(knn_predict(Xs[:200], y_tr, Xs[250:], best) == y_te)
    print(f"with a large-scale noise feature: raw acc={acc_raw:.4f}  standardised acc={acc_std:.4f}")


if __name__ == "__main__":
    main()
