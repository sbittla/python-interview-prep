"""
Exercise 09 — Regression Metrics: MSE, RMSE, MAE, R^2            [Tier: ★ Core]
Chapter 35 · Pattern: loss choice = which centre you estimate · Target time: 15 min

Problem
-------
1. ``mse``, ``rmse``, ``mae`` for equal-length, non-empty y_true / y_pred (else ValueError).
2. ``r2(y_true, y_pred)`` = 1 - SS_res / SS_tot, SS_res = sum((y - yhat)^2),
   SS_tot = sum((y - mean(y))^2). Convention when SS_tot == 0 (constant target):
   1.0 if the predictions are perfect, else 0.0 (scikit-learn's default ``force_finite``).
3. ``best_constant(y, loss)``: brute-force search over a fine grid for the constant c
   minimising MSE or MAE, to show MSE -> mean, MAE -> median.
4. ``mape``: mean(|y - yhat| / |y|); raise ValueError if any y == 0.

Examples
--------
>>> mse([3, -0.5, 2, 7], [2.5, 0.0, 2, 8]), mae([3, -0.5, 2, 7], [2.5, 0.0, 2, 8])
(0.375, 0.5)

Constraints
-----------
- Inputs are numeric 1-D sequences.

Approach ladder
---------------
Every metric is one O(n) vectorised pass. The "ladder" is choosing the metric:
1. MSE / RMSE — penalises large errors quadratically; minimised by the mean; RMSE is in
   the target's units. Outliers dominate.
2. MAE — linear penalty; minimised by the median; robust to outliers.
3. R^2 — scale-free: 0 = as good as predicting the mean, < 0 = worse, 1 = perfect.
``best_constant`` is O(n * G) for G grid points: a check, not a method.

Follow-ups
----------
- Why can R^2 be negative on a test set? The model can be worse than the test mean.
- Adjusted R^2 = 1 - (1 - R^2)(n - 1)/(n - p - 1) penalises extra features.
- Huber loss: quadratic near 0, linear in the tails.
- MAPE explodes near y = 0 and is asymmetric; prefer MAE or sMAPE with care.
- Edge cases: constant y_true, empty input, length mismatch, y == 0 in MAPE.
"""
from __future__ import annotations

import numpy as np


def _arrays(y_true, y_pred):
    a, b = np.asarray(y_true, float), np.asarray(y_pred, float)
    if a.shape != b.shape or a.size == 0:
        raise ValueError("need non-empty inputs of equal shape")
    return a, b


def mse(y_true, y_pred) -> float:
    a, b = _arrays(y_true, y_pred)
    return float(np.mean((a - b) ** 2))


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mse(y_true, y_pred)))


def mae(y_true, y_pred) -> float:
    a, b = _arrays(y_true, y_pred)
    return float(np.mean(np.abs(a - b)))


def r2(y_true, y_pred) -> float:
    a, b = _arrays(y_true, y_pred)
    ss_res = float(np.sum((a - b) ** 2))
    ss_tot = float(np.sum((a - a.mean()) ** 2))
    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0
    return 1 - ss_res / ss_tot


def mape(y_true, y_pred) -> float:
    a, b = _arrays(y_true, y_pred)
    if np.any(a == 0):
        raise ValueError("MAPE is undefined when a true value is 0")
    return float(np.mean(np.abs(a - b) / np.abs(a)))


def best_constant(y, loss: str, grid_step: float = 0.01) -> float:
    y = np.asarray(y, float)
    grid = np.arange(y.min(), y.max() + grid_step, grid_step)
    errs = [mse(y, np.full_like(y, c)) if loss == "mse" else mae(y, np.full_like(y, c)) for c in grid]
    return float(grid[int(np.argmin(errs))])


def main() -> None:
    yt, yp = [3, -0.5, 2, 7], [2.5, 0.0, 2, 8]
    print("mse", mse(yt, yp), " rmse", round(rmse(yt, yp), 4), " mae", mae(yt, yp), " r2", round(r2(yt, yp), 4))
    y = [1.0, 2.0, 2.0, 3.0, 50.0]                       # one outlier
    print("mean", np.mean(y), " median", np.median(y))
    print("best constant under MSE:", round(best_constant(y, "mse"), 2), " under MAE:", round(best_constant(y, "mae"), 2))
    print("r2 predicting the mean :", r2(y, np.full(5, np.mean(y))))
    print("r2 worse than the mean :", round(r2([1, 2, 3], [3, 2, 1]), 4))
    print("r2 constant target     :", r2([4, 4, 4], [4, 4, 4]), r2([4, 4, 4], [4, 5, 4]))
    print("mape                   :", round(mape([100, 200], [110, 180]), 4))
    try:
        mape([0, 1], [1, 1])
    except ValueError as e:
        print("mape with y=0 -> ValueError:", e)


if __name__ == "__main__":
    main()
