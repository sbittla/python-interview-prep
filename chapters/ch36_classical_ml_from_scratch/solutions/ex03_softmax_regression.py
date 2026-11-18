"""
Exercise 03 — Softmax (Multinomial Logistic) Regression              [Tier: ★ Core]
Chapter 36 · Pattern: GLM + gradient descent · Target time: 25 min

Problem
-------
Train a K-class linear classifier with softmax outputs and cross-entropy loss.

- ``softmax(Z)`` — row-wise, numerically stable;
- ``cross_entropy(P, y)`` — mean −log P[i, y_i];
- ``one_hot(y, k)``;
- ``fit(X, y, k, lr, epochs)`` returning (W, b, losses) with W of shape (d, k), b of shape (k,);
- ``predict`` and ``confusion_matrix``.

Examples
--------
>>> np.round(softmax(np.array([[1000.0, 1000.0, 0.0]])), 4).tolist()
[[0.5, 0.5, 0.0]]

Constraints
-----------
- NumPy only. Labels are integers in [0, k).

Approach ladder
---------------
1. Naive — exp(Z)/sum(exp(Z)): overflows (inf/inf = NaN) for logits ≳ 710.
2. Stable — subtract the row max before exponentiating (softmax is shift-invariant).
3. Efficient gradient — dL/dZ = (P − Y)/n; dW = Xᵀ(P − Y)/n. O(ndk) per epoch, fully vectorised;
   never loop over classes or samples.

Hints
-----
- For cross-entropy use log-softmax = Z − max − log Σ exp(Z − max) to avoid log(0).
- With k = 2, softmax regression is equivalent to logistic regression on the logit difference.

Follow-ups
----------
- Why is the softmax over-parameterised? (Adding the same vector to every column of W leaves P
  unchanged; regularisation or fixing one class to 0 removes the redundancy.)
- How do you turn this into a one-hidden-layer MLP? (Insert X → ReLU(XW₁+b₁) before the softmax.)
"""
from __future__ import annotations

import numpy as np

CENTERS = np.array([[0.0, 2.5], [-2.5, -1.5], [2.5, -1.5]])


def make_data(n_per_class: int = 80, seed: int = 0):
    rng = np.random.default_rng(seed)
    X = np.vstack([rng.normal(c, 1.0, size=(n_per_class, 2)) for c in CENTERS])
    y = np.repeat(np.arange(len(CENTERS)), n_per_class)
    perm = rng.permutation(len(y))
    return X[perm], y[perm]


def softmax(Z: np.ndarray) -> np.ndarray:
    Z = Z - Z.max(axis=1, keepdims=True)
    E = np.exp(Z)
    return E / E.sum(axis=1, keepdims=True)


def log_softmax(Z: np.ndarray) -> np.ndarray:
    Z = Z - Z.max(axis=1, keepdims=True)
    return Z - np.log(np.exp(Z).sum(axis=1, keepdims=True))


def one_hot(y: np.ndarray, k: int) -> np.ndarray:
    Y = np.zeros((len(y), k))
    Y[np.arange(len(y)), y] = 1.0
    return Y


def cross_entropy(P: np.ndarray, y: np.ndarray) -> float:
    eps = 1e-12
    return float(-np.mean(np.log(P[np.arange(len(y)), y] + eps)))


def fit(X: np.ndarray, y: np.ndarray, k: int, lr: float = 0.5, epochs: int = 200):
    n, d = X.shape
    W = np.zeros((d, k))
    b = np.zeros(k)
    Y = one_hot(y, k)
    losses = []
    for _ in range(epochs):
        Z = X @ W + b
        losses.append(float(-np.mean(np.sum(Y * log_softmax(Z), axis=1))))
        G = (softmax(Z) - Y) / n          # dL/dZ, shape (n, k)
        W -= lr * (X.T @ G)
        b -= lr * G.sum(axis=0)
    return W, b, losses


def predict(X: np.ndarray, W: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.argmax(X @ W + b, axis=1)


def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, k: int) -> np.ndarray:
    cm = np.zeros((k, k), dtype=int)
    np.add.at(cm, (y_true, y_pred), 1)
    return cm


def main() -> None:
    with np.errstate(all="ignore"):
        Z = np.array([[1000.0, 1000.0, 0.0]])
        naive = np.exp(Z) / np.exp(Z).sum(axis=1, keepdims=True)
    print("naive softmax:", naive.tolist())
    print("stable softmax:", np.round(softmax(Z), 4).tolist())
    print("shift invariance:", bool(np.allclose(softmax(np.array([[1.0, 2.0, 3.0]])),
                                               softmax(np.array([[101.0, 102.0, 103.0]])))))

    X, y = make_data()
    k = 3
    X_tr, y_tr, X_te, y_te = X[:180], y[:180], X[180:], y[180:]
    W, b, losses = fit(X_tr, y_tr, k)
    for t in (0, 10, 50, 199):
        print(f"  epoch {t:3d} loss={losses[t]:.4f}")
    print("initial loss equals log(3):", bool(np.isclose(losses[0], np.log(3))))
    P = softmax(X_te @ W + b)
    print(f"test cross-entropy={cross_entropy(P, y_te):.4f}")
    y_hat = predict(X_te, W, b)
    print(f"train acc={np.mean(predict(X_tr, W, b) == y_tr):.4f}  test acc={np.mean(y_hat == y_te):.4f}")
    print("confusion matrix (rows=true, cols=pred):")
    for row in confusion_matrix(y_te, y_hat, k):
        print("  ", row.tolist())

    # Two-class softmax == logistic regression on (z1 - z0)
    z = np.array([[0.3, 1.7]])
    sig = 1 / (1 + np.exp(-(z[0, 1] - z[0, 0])))
    print("2-class softmax p1 == sigmoid(z1-z0):", bool(np.isclose(softmax(z)[0, 1], sig)))


if __name__ == "__main__":
    main()
