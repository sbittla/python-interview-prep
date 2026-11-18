"""
Exercise 02 — Binary Logistic Regression with a Gradient Check        [Tier: ★ Core]
Chapter 36 · Pattern: GLM + gradient descent · Target time: 25 min

Problem
-------
Implement binary logistic regression from scratch:

- ``sigmoid(z)`` that never overflows for large |z|;
- ``bce_with_logits(z, y)`` — mean binary cross-entropy computed directly from logits;
- ``gradients(X, y, w, b)`` returning (∂L/∂w, ∂L/∂b);
- ``fit(X, y, lr, epochs)`` returning (w, b, losses);
- ``predict_proba`` / ``predict`` / ``accuracy``;
- ``numerical_gradient`` (central differences) to verify ``gradients``.

Examples
--------
>>> sigmoid(np.array([-1000.0, 0.0, 1000.0])).tolist()
[0.0, 0.5, 1.0]

Constraints
-----------
- NumPy only; no RuntimeWarnings from overflow.
- Labels are 0/1.

Approach ladder
---------------
1. Naive — p = 1/(1+exp(-z)) and loss = −mean(y log p + (1−y) log(1−p)). Overflows for z ≪ 0
   and gives log(0) = −inf once p rounds to exactly 0 or 1.
2. Stable — compute the loss from logits: log(1+e^{−|z|}) + max(z,0) − y·z, and a branch-free
   sigmoid using e^{−|z|}. Same O(nd) cost per epoch, no inf/NaN.
3. Verified — compare analytic gradients against central differences before trusting training.

Hints
-----
- ∂L/∂z = σ(z) − y, so ∂L/∂w = Xᵀ(p − y)/n and ∂L/∂b = mean(p − y).
- Central difference: (f(θ+h) − f(θ−h)) / 2h with h ≈ 1e-5.

Follow-ups
----------
- Why is the loss convex in (w, b)? What happens to w on perfectly separable data? (‖w‖ → ∞
  without regularisation.)
- How do you pick a threshold other than 0.5? (Precision/recall trade-off, Chapter 35.)
"""
from __future__ import annotations

import numpy as np


def make_data(n_per_class: int = 100, seed: int = 0):
    rng = np.random.default_rng(seed)
    X0 = rng.normal(loc=[-1.0, -1.0], scale=1.0, size=(n_per_class, 2))
    X1 = rng.normal(loc=[1.5, 1.0], scale=1.0, size=(n_per_class, 2))
    X = np.vstack([X0, X1])
    y = np.r_[np.zeros(n_per_class), np.ones(n_per_class)]
    perm = rng.permutation(len(y))
    return X[perm], y[perm]


def sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    e = np.exp(-np.abs(z))               # always in (0, 1]: no overflow
    return np.where(z >= 0, 1.0 / (1.0 + e), e / (1.0 + e))


def bce_with_logits(z: np.ndarray, y: np.ndarray) -> float:
    # log(1 + e^z) - y z, rewritten as max(z,0) + log1p(e^{-|z|}) - y z
    return float(np.mean(np.maximum(z, 0) + np.log1p(np.exp(-np.abs(z))) - y * z))


def gradients(X: np.ndarray, y: np.ndarray, w: np.ndarray, b: float):
    p = sigmoid(X @ w + b)
    r = p - y
    return X.T @ r / len(y), float(r.mean())


def numerical_gradient(X, y, w, b, h: float = 1e-5):
    def loss(w_, b_):
        return bce_with_logits(X @ w_ + b_, y)

    gw = np.zeros_like(w)
    for j in range(w.size):
        e = np.zeros_like(w)
        e[j] = h
        gw[j] = (loss(w + e, b) - loss(w - e, b)) / (2 * h)
    gb = (loss(w, b + h) - loss(w, b - h)) / (2 * h)
    return gw, gb


def fit(X: np.ndarray, y: np.ndarray, lr: float = 0.5, epochs: int = 300):
    w = np.zeros(X.shape[1])
    b = 0.0
    losses = []
    for _ in range(epochs):
        losses.append(bce_with_logits(X @ w + b, y))
        gw, gb = gradients(X, y, w, b)
        w -= lr * gw
        b -= lr * gb
    return w, b, losses


def predict_proba(X: np.ndarray, w: np.ndarray, b: float) -> np.ndarray:
    return sigmoid(X @ w + b)


def predict(X: np.ndarray, w: np.ndarray, b: float, threshold: float = 0.5) -> np.ndarray:
    return (predict_proba(X, w, b) >= threshold).astype(int)


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(y_true == y_pred))


def main() -> None:
    print("sigmoid([-1000, 0, 1000]):", sigmoid(np.array([-1000.0, 0.0, 1000.0])).tolist())
    with np.errstate(all="ignore"):
        naive = 1.0 / (1.0 + np.exp(-np.array([-1000.0])))
        p = np.array([1.0])
        naive_loss = -np.mean(0 * np.log(p) + 1 * np.log(1 - p))
    print("naive sigmoid(-1000):", naive.tolist(), "| naive BCE with p=1, y=0:", naive_loss)
    print(f"stable BCE with z=1000, y=0: {bce_with_logits(np.array([1000.0]), np.array([0.0])):.4f}")

    X, y = make_data()
    split = 150
    X_tr, y_tr, X_te, y_te = X[:split], y[:split], X[split:], y[split:]

    rng = np.random.default_rng(1)
    w0, b0 = rng.normal(size=2), 0.3
    ga, gba = gradients(X_tr, y_tr, w0, b0)
    gn, gbn = numerical_gradient(X_tr, y_tr, w0, b0)
    rel = np.linalg.norm(np.r_[ga, gba] - np.r_[gn, gbn]) / np.linalg.norm(np.r_[ga, gba] + np.r_[gn, gbn])
    print("analytic grad:", np.round(np.r_[ga, gba], 4).tolist())
    print("numeric  grad:", np.round(np.r_[gn, gbn], 4).tolist())
    print("gradient check relative error < 1e-7:", bool(rel < 1e-7))

    w, b, losses = fit(X_tr, y_tr, lr=0.5, epochs=300)
    for t in (0, 10, 100, 299):
        print(f"  epoch {t:3d} loss={losses[t]:.4f}")
    print("w:", np.round(w, 4).tolist(), "b:", round(b, 4))
    print(f"train acc={accuracy(y_tr, predict(X_tr, w, b)):.4f}  test acc={accuracy(y_te, predict(X_te, w, b)):.4f}")
    print("P(y=1) for points [-2,-2], [0,0], [2,2]:",
          np.round(predict_proba(np.array([[-2.0, -2.0], [0.0, 0.0], [2.0, 2.0]]), w, b), 4).tolist())


if __name__ == "__main__":
    main()
