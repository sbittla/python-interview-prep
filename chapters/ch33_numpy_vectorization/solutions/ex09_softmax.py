"""
Exercise 09 — Numerically Stable Softmax                         [Tier: ★ Core]
Chapter 33 · Pattern: shift-invariance / keepdims · Target time: 10 min

Problem
-------
Implement ``softmax(z, axis=-1, temperature=1.0)`` for an array of logits of any shape:

    softmax(z)_i = exp(z_i / T) / sum_j exp(z_j / T)

It must not overflow for logits like 1000 and must work along any axis. Also implement
``naive_softmax`` (the direct formula) to show where it breaks.

Examples
--------
>>> softmax(np.array([1.0, 2.0, 3.0])).round(4).tolist()
[0.09, 0.2447, 0.6652]
>>> softmax(np.array([1000.0, 1000.0])).tolist()
[0.5, 0.5]

Constraints
-----------
- temperature > 0.

Hints
-----
- softmax(z) == softmax(z - c) for any constant c. Pick c = max(z) so the largest exponent is 0.
- Use ``keepdims=True`` so the max and the sum broadcast back along ``axis``.

Approach ladder
---------------
1. Brute force — ``exp(z) / exp(z).sum()``: overflows to inf/inf = NaN for z > ~709.
2. Improved   — subtract the global max: fine for 1-D, wrong for batches (one row's max can
   underflow every other row to 0/0).
3. Optimal    — subtract the max *along the axis* with keepdims. O(n) time, O(n) space.

Follow-ups
----------
- What does temperature do as T → 0 and T → ∞? (argmax one-hot vs uniform)
- Why compute log-softmax directly instead of log(softmax(z))? (see Chapter 35)
"""
from __future__ import annotations

import numpy as np


def naive_softmax(z: np.ndarray, axis: int = -1) -> np.ndarray:
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


def global_max_softmax(z: np.ndarray, axis: int = -1) -> np.ndarray:
    e = np.exp(z - z.max())
    return e / e.sum(axis=axis, keepdims=True)


def softmax(z: np.ndarray, axis: int = -1, temperature: float = 1.0) -> np.ndarray:
    if temperature <= 0:
        raise ValueError("temperature must be > 0")
    z = np.asarray(z, dtype=float) / temperature
    shifted = z - z.max(axis=axis, keepdims=True)
    e = np.exp(shifted)
    return e / e.sum(axis=axis, keepdims=True)


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    z = np.array([1.0, 2.0, 3.0])
    print("softmax([1,2,3])      :", softmax(z))
    print("sums to 1             :", np.isclose(softmax(z).sum(), 1.0))
    print("shift invariance      :", np.allclose(softmax(z), softmax(z + 100)))

    big = np.array([1000.0, 1001.0, 1002.0])
    with np.errstate(over="ignore", invalid="ignore"):
        print("naive on [1000..1002] :", naive_softmax(big))
    print("stable on [1000..1002]:", softmax(big))

    print("\n== batch: per-row max matters ==")
    batch = np.array([[1000.0, 1001.0], [1.0, 2.0]])
    with np.errstate(invalid="ignore"):
        print("global-max version:\n", global_max_softmax(batch), sep="")
    print("per-row version   :\n", softmax(batch, axis=1), sep="")
    print("axis=0 columns sum:", softmax(batch, axis=0).sum(axis=0))

    print("\n== temperature ==")
    logits = np.array([2.0, 1.0, 0.1])
    for T in (0.1, 0.5, 1.0, 2.0, 100.0):
        print(f"T={T:<5} -> {softmax(logits, temperature=T)}")


if __name__ == "__main__":
    main()
