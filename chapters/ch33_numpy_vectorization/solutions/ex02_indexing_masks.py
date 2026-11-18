"""
Exercise 02 — Boolean and Fancy Indexing                         [Tier: ★ Core]
Chapter 33 · Pattern: masks / fancy indexing / argpartition · Target time: 15 min

Problem
-------
1. ``clip_outliers(x, k)``: return a copy of 1-D float array ``x`` where every value farther than
   ``k`` standard deviations from the mean is replaced by the median of ``x``. Do not modify ``x``.
2. ``top_k_indices(x, k)``: indices of the ``k`` largest values of ``x``, ordered from largest to
   smallest (ties broken by smaller index first). Must run in O(n + k log k).
3. ``gather_rows(X, rows, cols)``: given 2-D ``X`` and two equal-length index arrays, return
   ``[X[rows[0], cols[0]], X[rows[1], cols[1]], ...]`` without a loop.

Examples
--------
>>> clip_outliers(np.array([1., 2., 3., 100.]), 1.0).tolist()
[1.0, 2.0, 3.0, 2.5]
>>> top_k_indices(np.array([5, 1, 9, 9, 3]), 2).tolist()
[2, 3]
>>> gather_rows(np.arange(9).reshape(3, 3), np.array([0, 2]), np.array([1, 0])).tolist()
[1, 6]

Constraints
-----------
- 0 <= k <= len(x).

Hints
-----
- A boolean mask ``np.abs(x - mu) > k * sd`` selects the outliers; assignment through a mask
  writes into the array.
- ``np.argpartition(-x, k-1)[:k]`` gives the top-k in arbitrary order; sort only those k.
- Fancy indexing with two integer arrays pairs them element-wise.

Approach ladder
---------------
1. Brute force — ``np.argsort(-x)[:k]``: O(n log n). Python loop for outliers: O(n) slow steps.
2. Improved   — ``np.argsort(-x, kind="stable")[:k]`` gets the tie rule right but still sorts all n.
3. Optimal    — ``argpartition`` to find the k-th largest in O(n), then a stable sort of the k
   candidates with ``np.lexsort((idx, -values))``; ties at the boundary are handled by taking all
   values strictly greater than the threshold plus the lowest-index equal ones.

Follow-ups
----------
- Basic slicing returns a view; boolean/fancy indexing returns a copy. Why does it matter?
- How would you find top-k per row of a matrix? (``argpartition(..., axis=1)`` + ``take_along_axis``)
"""
from __future__ import annotations

import numpy as np


def clip_outliers(x: np.ndarray, k: float) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = x.copy()
    if x.size == 0:
        return out
    mu, sd = x.mean(), x.std()
    mask = np.abs(x - mu) > k * sd
    out[mask] = np.median(x)
    return out


def top_k_indices_sort(x: np.ndarray, k: int) -> np.ndarray:
    return np.argsort(-np.asarray(x), kind="stable")[:k]


def top_k_indices(x: np.ndarray, k: int) -> np.ndarray:
    x = np.asarray(x)
    if k <= 0:
        return np.array([], dtype=np.int64)
    if k >= x.size:
        return top_k_indices_sort(x, k)
    # k-th largest value (O(n) selection)
    thresh = x[np.argpartition(-x, k - 1)[k - 1]]
    greater = np.flatnonzero(x > thresh)
    equal = np.flatnonzero(x == thresh)[: k - greater.size]  # lowest indices win ties
    cand = np.concatenate([greater, equal])
    order = np.lexsort((cand, -x[cand]))  # primary: value desc, secondary: index asc
    return cand[order]


def gather_rows(X: np.ndarray, rows: np.ndarray, cols: np.ndarray) -> np.ndarray:
    return X[rows, cols]


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    a = np.arange(12).reshape(3, 4)
    print("a =\n", a, sep="")
    print("a[1]         :", a[1])
    print("a[:, 1]      :", a[:, 1])
    print("a[::2, ::-1] :\n", a[::2, ::-1], sep="")
    print("a[a % 2 == 0]:", a[a % 2 == 0])
    print("a[[0, 2]]    :\n", a[[0, 2]], sep="")
    print("a[[0, 2], [1, 3]]:", a[[0, 2], [1, 3]])

    print("\n== views vs copies ==")
    v = a[0, :2]
    v[0] = 99
    print("slice is a view, a[0,0] now:", a[0, 0])
    c = a[[0], :2]
    c[0, 0] = -1
    print("fancy is a copy, a[0,0] still:", a[0, 0])
    print("np.shares_memory(a, v):", np.shares_memory(a, v))

    print("\n== clip_outliers ==")
    x = np.array([1.0, 2.0, 3.0, 100.0])
    print("in :", x)
    print("out:", clip_outliers(x, 1.0))
    print("input untouched:", x)

    print("\n== top_k_indices ==")
    rng = np.random.default_rng(0)
    y = rng.integers(0, 10, size=12)
    print("y        :", y)
    for k in (0, 1, 3, 5, 12):
        fast = top_k_indices(y, k)
        print(f"k={k:<2} -> {fast.tolist()}  matches stable sort: "
              f"{np.array_equal(fast, top_k_indices_sort(y, k))}")

    print("\n== gather_rows ==")
    X = np.arange(9).reshape(3, 3)
    print(gather_rows(X, np.array([0, 2, 1]), np.array([1, 0, 2])))
    print("np.where(y > 5, y, 0):", np.where(y > 5, y, 0))


if __name__ == "__main__":
    main()
