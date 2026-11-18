"""
Exercise 05 — Aggregations Along Axes                            [Tier: ★ Core]
Chapter 33 · Pattern: axis reductions / bincount group-by · Target time: 15 min

Problem
-------
1. ``column_summary(X)``: for a 2-D float array that may contain NaN, return a dict with per-column
   ``mean``, ``std`` (population), ``min``, ``max`` ignoring NaNs, plus ``nan_count`` per column.
2. ``row_argmax_value(X)``: for each row return the column index of its max and the max itself.
3. ``group_sum(labels, values, n_groups)``: sum ``values`` per integer label 0..n_groups-1
   (a NumPy "group-by"), groups with no members get 0.
4. ``group_mean(labels, values, n_groups)``: mean per group; empty groups get NaN.

Examples
--------
>>> group_sum(np.array([0, 2, 0]), np.array([1., 5., 3.]), 3).tolist()
[4.0, 0.0, 5.0]
>>> row_argmax_value(np.array([[1, 9, 3], [7, 2, 7]]))[0].tolist()
[1, 0]

Constraints
-----------
- Labels are in [0, n_groups).

Hints
-----
- ``axis=0`` collapses rows (one result per column); ``axis=1`` collapses columns (one per row).
- ``np.nanmean``/``np.nanstd`` and ``np.isnan(X).sum(axis=0)``.
- ``np.bincount(labels, weights=values, minlength=n_groups)``.
- ``np.take_along_axis`` or ``X[np.arange(n), idx]``.

Approach ladder
---------------
1. Brute force — dictionary accumulation in a Python loop for group-by: O(n) Python steps.
2. Improved   — one boolean mask per group ``values[labels == g].sum()``: O(n * G).
3. Optimal    — ``np.bincount`` with weights: O(n + G) in C. (``np.add.at`` is the general
   unbuffered alternative for multi-dimensional targets.)

Follow-ups
----------
- What happens to ``X.sum(axis=0)`` shape vs ``keepdims=True``?
- Why does ``X[idx] += 1`` with repeated indices only add once? (buffered; use ``np.add.at``)
"""
from __future__ import annotations

import numpy as np


def column_summary(X: np.ndarray) -> dict:
    X = np.asarray(X, dtype=float)
    return {
        "mean": np.nanmean(X, axis=0),
        "std": np.nanstd(X, axis=0),
        "min": np.nanmin(X, axis=0),
        "max": np.nanmax(X, axis=0),
        "nan_count": np.isnan(X).sum(axis=0),
    }


def row_argmax_value(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.asarray(X)
    idx = X.argmax(axis=1)
    vals = np.take_along_axis(X, idx[:, None], axis=1)[:, 0]
    return idx, vals


def group_sum_loop(labels, values, n_groups):
    out = [0.0] * n_groups
    for g, v in zip(labels, values):
        out[g] += v
    return np.array(out)


def group_sum(labels: np.ndarray, values: np.ndarray, n_groups: int) -> np.ndarray:
    return np.bincount(labels, weights=values, minlength=n_groups).astype(float)


def group_mean(labels: np.ndarray, values: np.ndarray, n_groups: int) -> np.ndarray:
    sums = np.bincount(labels, weights=values, minlength=n_groups)
    counts = np.bincount(labels, minlength=n_groups)
    out = np.full(n_groups, np.nan)
    np.divide(sums, counts, out=out, where=counts > 0)
    return out


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    X = np.array([[1.0, 2.0, 3.0],
                  [4.0, np.nan, 6.0],
                  [7.0, 8.0, np.nan]])
    print("X =\n", X, sep="")
    print("X.sum(axis=0)          :", X.sum(axis=0), "(NaN poisons the plain sum)")
    print("np.nansum(X, axis=0)   :", np.nansum(X, axis=0))
    print("np.nansum(X, axis=1)   :", np.nansum(X, axis=1))
    print("keepdims shape         :", np.nansum(X, axis=1, keepdims=True).shape)
    for k, v in column_summary(X).items():
        print(f"{k:<10}: {v}")

    print("\n== row_argmax_value ==")
    M = np.array([[1, 9, 3], [7, 2, 7], [0, 0, 5]])
    idx, vals = row_argmax_value(M)
    print("argmax per row:", idx, " values:", vals, "(ties -> first index)")

    print("\n== group-by with bincount ==")
    rng = np.random.default_rng(7)
    labels = rng.integers(0, 4, size=1_000)
    values = rng.normal(10, 2, size=1_000)
    gs = group_sum(labels, values, 5)   # group 4 is empty
    print("group sums :", gs)
    print("loop agrees:", np.allclose(gs, group_sum_loop(labels, values, 5)))
    print("group means:", group_mean(labels, values, 5))

    print("\n== the repeated-index trap ==")
    counts = np.zeros(3, dtype=int)
    idx = np.array([0, 0, 2])
    counts[idx] += 1
    print("counts[idx] += 1  ->", counts)
    counts = np.zeros(3, dtype=int)
    np.add.at(counts, idx, 1)
    print("np.add.at         ->", counts)


if __name__ == "__main__":
    main()
