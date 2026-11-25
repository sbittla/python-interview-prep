"""
Exercise 02 — Gradient Check by Finite Differences               [Tier: ★ Core]
Chapter 35 · Pattern: matrix calculus + numerical verification · Target time: 20 min

Problem
-------
You derived a gradient by hand. Prove it before you train with it.

1. ``numerical_grad(f, w, eps=1e-5, method="central")``: estimate grad f(w) for a scalar
   function of a float64 vector by perturbing one coordinate at a time.
2. ``relative_error(a, b)`` = ||a - b|| / max(||a|| + ||b||, 1e-12).
3. Analytic gradients (X is n x d, y is length n, w is length d):
   - ``mse_loss`` L(w) = ||Xw - y||^2 / (2n), gradient X^T (Xw - y) / n.
   - ``logistic_loss`` L(w) = mean(log(1 + exp(z)) - y*z), z = Xw, y in {0, 1};
     gradient X^T (sigmoid(z) - y) / n.
4. ``check_gradient(f, grad, w)`` returns the relative error; below ~1e-7 passes in float64.

Examples
--------
>>> X = np.array([[1.0, 2.0], [3.0, 4.0]]); y = np.array([1.0, 0.0])
>>> mse_grad(np.zeros(2), X, y).tolist()      # X^T(0 - y)/2
[-0.5, -1.0]

Constraints
-----------
- float64 only: in float32 the round-off term eps_machine / eps swamps the check.

Hints
-----
- Perturb one coordinate at a time with a basis vector eps * e_i; never mutate w in place.
- Central difference: (f(w + eps e_i) - f(w - eps e_i)) / (2 eps).
- For the logistic loss, write log(1 + e^z) as max(z, 0) + log1p(exp(-|z|)).
- Chain rule for L = mean(g(Xw)): grad = X^T g'(Xw) / n.

Wrong-but-tempting
------------------
- Comparing absolute errors: a gradient of size 1e4 with error 1e-3 is fine; use relative.
- eps = 1e-12: round-off dominates and a correct gradient "fails".
- Checking in float32: expect only ~1e-3 relative agreement.

Follow-ups
----------
- Why central beats forward: Taylor terms of order eps cancel.
- Too-small eps: round-off error ~ eps_machine * |f| / eps grows (see the eps sweep).
- Check a random subset of coordinates when d is millions.
- Non-differentiable points (ReLU at 0, abs): the check may fail legitimately.
"""
from __future__ import annotations

from typing import Callable

import numpy as np


def numerical_grad(f: Callable[[np.ndarray], float], w: np.ndarray, eps: float = 1e-5,
                   method: str = "central") -> np.ndarray:
    raise NotImplementedError("TODO")


def relative_error(a: np.ndarray, b: np.ndarray) -> float:
    raise NotImplementedError("TODO")


def mse_loss(w, X, y) -> float:
    raise NotImplementedError("TODO")


def mse_grad(w, X, y) -> np.ndarray:
    raise NotImplementedError("TODO")


def _softplus(z):
    return np.maximum(z, 0) + np.log1p(np.exp(-np.abs(z)))   # log(1 + e^z) without overflow


def _sigmoid(z):
    return np.exp(-_softplus(-z))                             # 1 / (1 + e^-z), stable


def logistic_loss(w, X, y) -> float:
    raise NotImplementedError("TODO")


def logistic_grad(w, X, y) -> np.ndarray:
    raise NotImplementedError("TODO")


def check_gradient(f, grad, w, eps: float = 1e-5) -> float:
    raise NotImplementedError("TODO")


def main() -> None:
    rng = np.random.default_rng(35)
    X = rng.normal(size=(50, 4))
    y_reg = X @ np.array([1.0, -2.0, 0.5, 3.0]) + rng.normal(scale=0.1, size=50)
    y_cls = (rng.random(50) < 0.5).astype(float)
    w = rng.normal(size=4)

    print("mse      rel error:", f"{check_gradient(lambda v: mse_loss(v, X, y_reg), lambda v: mse_grad(v, X, y_reg), w):.0e}")
    print("logistic rel error:", f"{check_gradient(lambda v: logistic_loss(v, X, y_cls), lambda v: logistic_grad(v, X, y_cls), w):.0e}")
    buggy = lambda v: X.T @ (X @ v - y_reg)            # forgot the 1/n
    err = check_gradient(lambda v: mse_loss(v, X, y_reg), buggy, w)
    print("buggy (no 1/n) rel error:", round(err, 3), "-> caught:", err > 1e-4)
    bug2 = lambda v: X.T @ (_sigmoid(X @ v) - y_cls)[::-1] / len(y_cls)   # misaligned labels
    print("misaligned labels caught:", check_gradient(lambda v: logistic_loss(v, X, y_cls), bug2, w) > 1e-4)

    print("eps sweep on f(x) = exp(x) at x = 1 (true derivative e):")
    f = lambda v: float(np.exp(v[0]))
    for eps in (1e-1, 1e-3, 1e-5, 1e-8, 1e-11):
        fwd = abs(numerical_grad(f, np.array([1.0]), eps, "forward")[0] - np.e)
        cen = abs(numerical_grad(f, np.array([1.0]), eps, "central")[0] - np.e)
        print(f"  eps={eps:.0e}  forward err={fwd:.0e}  central err={cen:.0e}")


if __name__ == "__main__":
    main()
