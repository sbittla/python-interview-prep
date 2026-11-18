"""
Exercise 01 — Linear Regression: Normal Equation and Gradient Descent   [Tier: ★ Core]
Chapter 36 · Pattern: closed form vs iterative optimisation · Target time: 25 min

Problem
-------
Fit y ≈ X w + b on a synthetic dataset two ways:

1. ``fit_normal_equation(X, y)`` — solve the normal equations (Xbᵀ Xb) θ = Xbᵀ y where Xb is X
   with a column of ones appended, and return ``(w, b)``.
2. ``fit_gradient_descent(X, y, lr, epochs)`` — full-batch gradient descent on the mean squared
   error, returning ``(w, b, losses)`` where ``losses[t]`` is the MSE before update t.

Also implement ``predict``, ``mse`` and ``r2_score``. Show that the two fits agree.

Examples
--------
>>> X = np.array([[0.0], [1.0], [2.0]]); y = np.array([1.0, 3.0, 5.0])
>>> w, b = fit_normal_equation(X, y)
>>> np.round(w, 4).tolist(), round(float(b), 4)
([2.0], 1.0)

Constraints
-----------
- NumPy only. X has shape (n, d), y has shape (n,).
- Do not form an explicit matrix inverse.

Approach ladder
---------------
1. Brute force — θ = inv(XbᵀXb) Xbᵀy. O(nd² + d³), numerically fragile when XbᵀXb is
   ill-conditioned (inverse squares the condition number's damage).
2. Improved   — np.linalg.solve on the normal equations: same complexity, no explicit inverse.
   (np.linalg.lstsq / QR is the most stable choice and handles rank deficiency.)
3. Iterative  — gradient descent: O(nd) per epoch, O(d) memory beyond the data. This is what you
   use when d is huge or the data streams in mini-batches, and it generalises to every model
   in this chapter that has no closed form.

Hints
-----
- MSE L = (1/n)·Σ (ŷᵢ − yᵢ)²; ∂L/∂w = (2/n)·Xᵀ(ŷ − y); ∂L/∂b = (2/n)·Σ(ŷ − y).
- Standardise features before gradient descent or you will need a tiny learning rate.
- R² = 1 − SS_res / SS_tot.

Follow-ups
----------
- What happens if two columns of X are identical? (XᵀX is singular; solve fails, lstsq works.)
- How would you add L2 regularisation to the closed form? (Add λI to XᵀX, not on the bias.)
"""
from __future__ import annotations

import numpy as np

TRUE_W = np.array([2.0, -3.0, 0.5])
TRUE_B = 4.0


def make_data(n: int = 200, noise: float = 0.5, seed: int = 0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, TRUE_W.size))
    y = X @ TRUE_W + TRUE_B + noise * rng.normal(size=n)
    return X, y


def _with_bias(X: np.ndarray) -> np.ndarray:
    return np.hstack([X, np.ones((X.shape[0], 1))])


def fit_normal_equation_inverse(X: np.ndarray, y: np.ndarray):
    """Rung 1: explicit inverse (shown for comparison only)."""
    Xb = _with_bias(X)
    theta = np.linalg.inv(Xb.T @ Xb) @ Xb.T @ y
    return theta[:-1], theta[-1]


def fit_normal_equation(X: np.ndarray, y: np.ndarray):
    """Solve (XbᵀXb) θ = Xbᵀy; return (w, b)."""
    Xb = _with_bias(X)
    theta = np.linalg.solve(Xb.T @ Xb, Xb.T @ y)
    return theta[:-1], theta[-1]


def predict(X: np.ndarray, w: np.ndarray, b: float) -> np.ndarray:
    return X @ w + b


def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean((y_true - y_pred) ** 2))


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    return float(1.0 - ss_res / ss_tot)


def fit_gradient_descent(X: np.ndarray, y: np.ndarray, lr: float = 0.1, epochs: int = 500):
    """Full-batch gradient descent on MSE; return (w, b, losses)."""
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    losses = []
    for _ in range(epochs):
        err = X @ w + b - y               # (n,)
        losses.append(float(np.mean(err ** 2)))
        grad_w = (2.0 / n) * (X.T @ err)  # (d,)
        grad_b = (2.0 / n) * err.sum()
        w -= lr * grad_w
        b -= lr * grad_b
    return w, b, losses


def main() -> None:
    X, y = make_data()
    print("true w:", np.round(TRUE_W, 4).tolist(), "b:", TRUE_B)

    w_ne, b_ne = fit_normal_equation(X, y)
    print("normal equation w:", np.round(w_ne, 4).tolist(), "b:", round(float(b_ne), 4))

    w_inv, b_inv = fit_normal_equation_inverse(X, y)
    print("inverse agrees with solve:", bool(np.allclose(np.r_[w_inv, b_inv], np.r_[w_ne, b_ne])))

    w_gd, b_gd, losses = fit_gradient_descent(X, y, lr=0.1, epochs=500)
    print("gradient descent w:", np.round(w_gd, 4).tolist(), "b:", round(float(b_gd), 4))
    for t in (0, 10, 50, 100, 499):
        print(f"  epoch {t:3d} mse={losses[t]:.4f}")
    diff = np.max(np.abs(np.r_[w_gd, b_gd] - np.r_[w_ne, b_ne]))
    print("max |GD - closed form| < 1e-6:", bool(diff < 1e-6))

    y_hat = predict(X, w_ne, b_ne)
    print(f"train mse={mse(y, y_hat):.4f} r2={r2_score(y, y_hat):.4f}")

    # Edge case: duplicated column -> singular XᵀX; solve fails, lstsq still works.
    X_dup = np.hstack([X, X[:, :1]])
    try:
        fit_normal_equation(X_dup, y)
        print("solve on duplicated column: ok")
    except np.linalg.LinAlgError as exc:
        print("solve on duplicated column: LinAlgError:", exc)
    theta, *_ = np.linalg.lstsq(_with_bias(X_dup), y, rcond=None)
    print("lstsq minimum-norm w:", np.round(theta[:-1], 4).tolist())

    # Learning rate too large -> divergence.
    _, _, bad = fit_gradient_descent(X, y, lr=1.5, epochs=20)
    print("lr=1.5 loss at epoch 0, 10, 19:", [f"{bad[t]:.4g}" for t in (0, 10, 19)])


if __name__ == "__main__":
    main()
