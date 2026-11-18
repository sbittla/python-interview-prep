"""
Exercise 08 — Gaussian Naive Bayes                                    [Tier: ★ Core]
Chapter 36 · Pattern: generative classifier in log space · Target time: 20 min

Problem
-------
Implement Gaussian naive Bayes for continuous features.

- ``fit(X, y, var_smoothing)`` → dict with ``classes``, ``log_prior`` (C,), ``mean`` (C, d),
  ``var`` (C, d). Add ``var_smoothing * max(feature variance)`` to every variance.
- ``joint_log_likelihood(model, X)`` → (n, C) matrix of log p(c) + Σ_j log N(x_j; μ_cj, σ²_cj).
- ``predict_proba(model, X)`` — normalise with log-sum-exp; ``predict(model, X)``.

Examples
--------
>>> X = np.array([[0.0], [0.2], [5.0], [5.2]]); y = np.array([0, 0, 1, 1])
>>> predict(fit(X, y), np.array([[0.1], [4.9]])).tolist()
[0, 1]

Constraints
-----------
- NumPy only. Never multiply raw probabilities (underflow); work in log space.

Approach ladder
---------------
1. Naive — multiply d Gaussian densities per class: underflows to 0 for moderate d, giving 0/0.
2. Log space — sum log densities; O(n·C·d) prediction, O(n·d) training (one pass for means and
   variances). Normalise with log-sum-exp.
3. Smoothing — add a small fraction of the largest variance so a constant feature in one class
   does not produce division by zero / infinite log-likelihoods.

Hints
-----
- log N(x; μ, σ²) = −½ log(2πσ²) − (x − μ)² / (2σ²).
- logsumexp(a) = m + log Σ exp(a − m) with m = max(a).

Follow-ups
----------
- The "naive" assumption is conditional independence of features given the class. Why does NB
  still classify well when it is violated? (Decision only needs the argmax to be right, even if the
  probabilities are poorly calibrated.)
- Gaussian NB has a quadratic decision boundary; with shared variances it becomes linear (like LDA).
"""
from __future__ import annotations

import numpy as np


def make_data(n_per: int = 100, seed: int = 0):
    rng = np.random.default_rng(seed)
    means = np.array([[0.0, 0.0, 0.0], [2.0, 2.0, 0.0], [0.0, 3.0, 2.0]])
    scales = np.array([[1.0, 0.5, 1.0], [0.7, 1.0, 1.0], [1.0, 1.0, 0.5]])
    X = np.vstack([rng.normal(m, s, size=(n_per, 3)) for m, s in zip(means, scales)])
    y = np.repeat(np.arange(3), n_per)
    perm = rng.permutation(len(y))
    return X[perm], y[perm]


def fit(X: np.ndarray, y: np.ndarray, var_smoothing: float = 1e-9) -> dict:
    classes = np.unique(y)
    eps = var_smoothing * X.var(axis=0).max()
    mean = np.array([X[y == c].mean(axis=0) for c in classes])
    var = np.array([X[y == c].var(axis=0) for c in classes]) + eps
    prior = np.array([np.mean(y == c) for c in classes])
    return {"classes": classes, "log_prior": np.log(prior), "mean": mean, "var": var}


def joint_log_likelihood(model: dict, X: np.ndarray) -> np.ndarray:
    mu, var = model["mean"], model["var"]                         # (C, d)
    diff = X[:, None, :] - mu[None, :, :]                          # (n, C, d)
    ll = -0.5 * np.log(2 * np.pi * var)[None] - diff ** 2 / (2 * var[None])
    return model["log_prior"][None, :] + ll.sum(axis=2)


def _logsumexp(a: np.ndarray, axis: int = 1) -> np.ndarray:
    m = a.max(axis=axis, keepdims=True)
    return m + np.log(np.exp(a - m).sum(axis=axis, keepdims=True))


def predict_proba(model: dict, X: np.ndarray) -> np.ndarray:
    jll = joint_log_likelihood(model, X)
    return np.exp(jll - _logsumexp(jll))


def predict(model: dict, X: np.ndarray) -> np.ndarray:
    return model["classes"][np.argmax(joint_log_likelihood(model, X), axis=1)]


def main() -> None:
    X, y = make_data()
    X_tr, y_tr, X_te, y_te = X[:240], y[:240], X[240:], y[240:]
    model = fit(X_tr, y_tr)
    print("priors:", np.round(np.exp(model["log_prior"]), 4).tolist())
    print("class means:")
    for c, m in zip(model["classes"], model["mean"]):
        print(f"  class {c}: {np.round(m, 4).tolist()}")
    print(f"train acc={np.mean(predict(model, X_tr) == y_tr):.4f} test acc={np.mean(predict(model, X_te) == y_te):.4f}")
    P = predict_proba(model, X_te[:3])
    print("first 3 test probabilities:", np.round(P, 4).tolist(), "rows sum to 1:", bool(np.allclose(P.sum(1), 1)))

    # Underflow: 400 features of tiny densities
    rng = np.random.default_rng(1)
    Xw = rng.normal(size=(20, 400))
    yw = np.r_[np.zeros(10, int), np.ones(10, int)]
    Xw[yw == 1] += 0.5
    mw = fit(Xw, yw)
    x = Xw[:1]
    dens = np.exp(-0.5 * np.log(2 * np.pi * mw["var"]) - (x - mw["mean"]) ** 2 / (2 * mw["var"]))
    print("naive product of 400 densities per class:", np.prod(dens, axis=1).tolist())
    print("log-space joint log-likelihoods:", np.round(joint_log_likelihood(mw, x), 4).tolist())

    # Constant feature inside one class -> zero variance without smoothing
    Xc = np.array([[1.0, 0.0], [1.0, 1.0], [3.0, 0.5], [4.0, 0.7]])
    yc = np.array([0, 0, 1, 1])
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = fit(Xc, yc, var_smoothing=0.0)
        print("no smoothing, class-0 var:", raw["var"][0].tolist(),
              "jll:", joint_log_likelihood(raw, np.array([[1.5, 0.5]])).tolist())
    sm = fit(Xc, yc, var_smoothing=1e-2)
    print("with smoothing prediction for [1.5, 0.5]:", predict(sm, np.array([[1.5, 0.5]])).tolist())


if __name__ == "__main__":
    main()
