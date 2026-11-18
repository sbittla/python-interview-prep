"""
Exercise 04 — Vectorising Loops (with equality checks)           [Tier: ★ Core]
Chapter 33 · Pattern: loop → ufunc / where / cumsum · Target time: 20 min

Problem
-------
Each task below comes with a reference Python loop. Write the vectorised version and prove it
returns exactly the same result.

1. ``piecewise(x)``: f(x) = x**2 if x < 0; 2*x if 0 <= x < 5; 10 otherwise.
2. ``rowwise_dot(A, B)``: for two (n, d) arrays return the length-n vector of row dot products.
3. ``count_sign_changes(x)``: number of indices i with sign(x[i]) != sign(x[i-1]) (zeros count as
   their own sign).
4. ``running_max_drawdown(prices)``: largest drop from a running peak, ``max(peak_i - price_i)``.

Examples
--------
>>> piecewise(np.array([-2., 1., 7.])).tolist()
[4.0, 2.0, 10.0]
>>> count_sign_changes(np.array([1, -1, -2, 0, 3]))
3
>>> running_max_drawdown(np.array([3., 5., 1., 4., 0.5]))
4.5

Constraints
-----------
- Arrays up to 10^6 elements; must be O(n) with no Python-level loop.

Hints
-----
- ``np.select([cond1, cond2], [val1, val2], default)`` or nested ``np.where``.
- ``np.einsum("ij,ij->i", A, B)`` or ``(A * B).sum(axis=1)``.
- ``np.diff(np.sign(x)) != 0``.
- ``np.maximum.accumulate`` is a running max.

Approach ladder
---------------
1. Brute force — the Python loops given (O(n), but ~50-100x slower in constant factor).
2. Improved   — ``np.vectorize`` — looks vectorised, but it is a Python loop in disguise.
3. Optimal    — whole-array ufuncs: ``np.select``, ``einsum``, ``np.diff``, ``ufunc.accumulate``.

Follow-ups
----------
- Which loops are *hard* to vectorise? (true sequential dependencies, e.g. an IIR filter;
  some have an ``accumulate`` trick, others need numba or a rewrite.)
- Why is ``np.vectorize`` not a speedup?
"""
from __future__ import annotations

import time

import numpy as np


# ---- reference loops -------------------------------------------------------
def piecewise_loop(x):
    out = np.empty(len(x), dtype=float)
    for i, v in enumerate(x):
        if v < 0:
            out[i] = v * v
        elif v < 5:
            out[i] = 2 * v
        else:
            out[i] = 10.0
    return out


def rowwise_dot_loop(A, B):
    return np.array([sum(a * b for a, b in zip(ra, rb)) for ra, rb in zip(A, B)], dtype=float)


def count_sign_changes_loop(x):
    count = 0
    for i in range(1, len(x)):
        if np.sign(x[i]) != np.sign(x[i - 1]):
            count += 1
    return count


def running_max_drawdown_loop(prices):
    peak, best = -np.inf, 0.0
    for p in prices:
        peak = max(peak, p)
        best = max(best, peak - p)
    return float(best)


# ---- vectorised ------------------------------------------------------------
def piecewise(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return np.select([x < 0, x < 5], [x * x, 2 * x], default=10.0)


def rowwise_dot(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return np.einsum("ij,ij->i", np.asarray(A, float), np.asarray(B, float))


def count_sign_changes(x: np.ndarray) -> int:
    s = np.sign(np.asarray(x))
    return int(np.count_nonzero(s[1:] != s[:-1]))


def running_max_drawdown(prices: np.ndarray) -> float:
    p = np.asarray(prices, dtype=float)
    if p.size == 0:
        return 0.0
    peak = np.maximum.accumulate(p)
    return float((peak - p).max())


def _faster(fast, slow, *args, repeats=3) -> bool:
    def best(fn):
        times = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            fn(*args)
            times.append(time.perf_counter() - t0)
        return min(times)
    return best(fast) < best(slow)


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    rng = np.random.default_rng(42)
    x = rng.normal(2, 4, size=20_000)
    A = rng.normal(size=(2_000, 8))
    B = rng.normal(size=(2_000, 8))
    walk = 100 + np.cumsum(rng.normal(size=5_000))

    print("== piecewise ==")
    print("sample in :", x[:5])
    print("sample out:", piecewise(x[:5]))
    print("equal to loop:", np.allclose(piecewise(x), piecewise_loop(x)))

    print("\n== rowwise_dot ==")
    print("first 3:", rowwise_dot(A, B)[:3])
    print("equal to loop:", np.allclose(rowwise_dot(A, B), rowwise_dot_loop(A, B)))
    print("equal to (A*B).sum(1):", np.allclose(rowwise_dot(A, B), (A * B).sum(axis=1)))

    print("\n== count_sign_changes ==")
    print("tiny example:", count_sign_changes(np.array([1, -1, -2, 0, 3])))
    print("vectorised:", count_sign_changes(x), " loop:", count_sign_changes_loop(x))

    print("\n== running_max_drawdown ==")
    print("tiny example:", running_max_drawdown(np.array([3.0, 5.0, 1.0, 4.0, 0.5])))
    print("vectorised:", round(running_max_drawdown(walk), 4),
          " loop:", round(running_max_drawdown_loop(walk), 4))
    print("empty:", running_max_drawdown(np.array([])))

    print("\n== np.vectorize is still a loop ==")
    vec = np.vectorize(lambda v: v * v if v < 0 else (2 * v if v < 5 else 10.0))
    print("np.vectorize equal:", np.allclose(vec(x), piecewise(x)))
    print("np.select faster than np.vectorize:", _faster(piecewise, vec, x))
    print("np.select faster than python loop :", _faster(piecewise, piecewise_loop, x))


if __name__ == "__main__":
    main()
