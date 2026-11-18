"""
Exercise 10 — Moving Average Three Ways                          [Tier: ★ Core]
Chapter 33 · Pattern: prefix sums / convolution / sliding windows · Target time: 15 min

Problem
-------
``moving_average(x, w)`` returns the simple moving average of a 1-D array over windows of size
``w`` in "valid" mode: output length ``len(x) - w + 1``, ``out[i] = mean(x[i:i+w])``.
Raise ``ValueError`` if ``w < 1`` or ``w > len(x)``.

Also implement ``ewma(x, alpha)`` (exponentially weighted moving average,
``s[0] = x[0]; s[t] = alpha*x[t] + (1-alpha)*s[t-1]``) — a loop with a true sequential dependency.

Examples
--------
>>> moving_average(np.array([1., 2., 3., 4., 5.]), 2).tolist()
[1.5, 2.5, 3.5, 4.5]

Constraints
-----------
- len(x) up to 10^7; w up to len(x).

Hints
-----
- Prefix sums: ``c = np.cumsum(np.insert(x, 0, 0))``; window sum = ``c[i+w] - c[i]``.
- ``np.convolve(x, np.ones(w)/w, mode="valid")``.
- ``np.lib.stride_tricks.sliding_window_view(x, w).mean(axis=1)`` (O(n*w)).

Approach ladder
---------------
1. Brute force — mean of each slice in a loop: O(n*w).
2. Improved   — ``sliding_window_view(x, w).mean(1)``: vectorised but still O(n*w) work;
   ``np.convolve``: O(n*w) direct (fine for small w).
3. Optimal    — prefix sums: O(n) regardless of w. Caveat: large cumulative sums lose precision for
   long float32 series; use float64 or periodic re-anchoring.

Follow-ups
----------
- Centred vs trailing windows; "same" mode padding.
- Can EWMA be vectorised? (yes, with powers of (1-alpha) — but it underflows for long series;
  in practice use the loop, pandas ``ewm`` or ``scipy.signal.lfilter``.)
"""
from __future__ import annotations

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def _check(x, w):
    if w < 1 or w > len(x):
        raise ValueError("window must satisfy 1 <= w <= len(x)")


def moving_average_loop(x, w):
    _check(x, w)
    return np.array([x[i:i + w].mean() for i in range(len(x) - w + 1)])


def moving_average_convolve(x, w):
    _check(x, w)
    return np.convolve(x, np.ones(w) / w, mode="valid")


def moving_average_windows(x, w):
    _check(x, w)
    return sliding_window_view(x, w).mean(axis=1)


def moving_average(x: np.ndarray, w: int) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    _check(x, w)
    c = np.cumsum(np.insert(x, 0, 0.0))
    return (c[w:] - c[:-w]) / w


def ewma(x: np.ndarray, alpha: float) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.empty_like(x)
    if x.size == 0:
        return out
    out[0] = x[0]
    for t in range(1, x.size):
        out[t] = alpha * x[t] + (1 - alpha) * out[t - 1]
    return out


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    print("x =", x)
    print("w=2 prefix  :", moving_average(x, 2))
    print("w=3 convolve:", moving_average_convolve(x, 3))
    print("w=5 windows :", moving_average_windows(x, 5))
    print("windows view (w=3):\n", sliding_window_view(x, 3), sep="")

    rng = np.random.default_rng(3)
    s = np.cumsum(rng.normal(size=2_000))
    ref = moving_average_loop(s, 50)
    print("\nprefix   == loop:", np.allclose(moving_average(s, 50), ref))
    print("convolve == loop:", np.allclose(moving_average_convolve(s, 50), ref))
    print("windows  == loop:", np.allclose(moving_average_windows(s, 50), ref))
    try:
        moving_average(x, 6)
    except ValueError as e:
        print("w > n -> ValueError:", e)

    print("\n== ewma ==")
    print("ewma(x, 0.5):", ewma(x, 0.5))
    print("ewma(x, 1.0) == x:", np.array_equal(ewma(x, 1.0), x))


if __name__ == "__main__":
    main()
