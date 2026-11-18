"""
Exercise 03 — Broadcasting Rules                                 [Tier: ★ Core]
Chapter 33 · Pattern: broadcasting · Target time: 15 min

Problem
-------
1. ``broadcast_shape(s1, s2)``: implement NumPy's broadcasting rule for two shapes (tuples).
   Return the result shape, or raise ``ValueError`` if they are incompatible.
2. ``standardize_columns(X)``: return ``(X - mean) / std`` per column of a 2-D array; columns with
   zero standard deviation become all zeros (no division warnings).
3. ``outer_op(a, b, op)``: for 1-D ``a`` (len m) and ``b`` (len n) return the (m, n) table
   ``op(a[i], b[j])`` using broadcasting. ``op`` is a NumPy ufunc such as ``np.add``.

Examples
--------
>>> broadcast_shape((3, 1), (1, 4))
(3, 4)
>>> broadcast_shape((8, 1, 6, 1), (7, 1, 5))
(8, 7, 6, 5)
>>> outer_op(np.array([1, 2]), np.array([10, 20, 30]), np.add).tolist()
[[11, 21, 31], [12, 22, 32]]

Constraints
-----------
- Shapes have length 0..8; dimensions are non-negative ints.

Hints
-----
- Right-align the shapes; pad the shorter one with leading 1s.
- Two dims are compatible if they are equal or one of them is 1. The result is the max (or 0 when
  the other is 1 and this one is 0).
- ``a[:, None]`` has shape (m, 1); ``b[None, :]`` has shape (1, n).

Approach ladder
---------------
1. Brute force — for ``outer_op``, a double loop: O(mn) Python steps.
2. Improved   — ``np.tile``/``np.repeat`` both operands to (m, n) then apply op: vectorised but
   materialises two extra (m, n) arrays.
3. Optimal    — broadcasting ``op(a[:, None], b[None, :])``: no copies of the inputs, one output.

Follow-ups
----------
- Why does ``(3,) + (3, 1)`` give (3, 3) and not an error? Many bugs come from this.
- What does ``keepdims=True`` buy you when normalising rows?
"""
from __future__ import annotations

import numpy as np


def broadcast_shape(s1: tuple, s2: tuple) -> tuple:
    n = max(len(s1), len(s2))
    a = (1,) * (n - len(s1)) + tuple(s1)
    b = (1,) * (n - len(s2)) + tuple(s2)
    out = []
    for i, (x, y) in enumerate(zip(a, b)):
        if x == y or y == 1:
            out.append(x)
        elif x == 1:
            out.append(y)
        else:
            raise ValueError(f"shapes {s1} and {s2} are not broadcastable (dim {i}: {x} vs {y})")
    return tuple(out)


def standardize_columns(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=float)
    mu = X.mean(axis=0, keepdims=True)          # (1, d)
    sd = X.std(axis=0, keepdims=True)           # (1, d)
    safe = np.where(sd == 0, 1.0, sd)
    return (X - mu) / safe                      # (n, d) op (1, d) -> (n, d)


def outer_op_loop(a, b, op):
    return np.array([[op(x, y) for y in b] for x in a])


def outer_op(a: np.ndarray, b: np.ndarray, op) -> np.ndarray:
    return op(np.asarray(a)[:, None], np.asarray(b)[None, :])


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    print("== broadcast_shape vs np.broadcast_shapes ==")
    cases = [((3, 1), (1, 4)), ((8, 1, 6, 1), (7, 1, 5)), ((5,), ()), ((0,), (1,)),
             ((2, 3), (3,)), ((2, 3), (2,))]
    for s1, s2 in cases:
        try:
            mine = broadcast_shape(s1, s2)
        except ValueError:
            mine = "ValueError"
        try:
            ref = np.broadcast_shapes(s1, s2)
        except ValueError:
            ref = "ValueError"
        print(f"{str(s1):>14} with {str(s2):<10} -> {str(mine):<14} numpy agrees: {mine == ref}")

    print("\n== the classic (3,) + (3, 1) surprise ==")
    v = np.array([1, 2, 3])
    print((v + v.reshape(3, 1)))

    print("\n== standardize_columns ==")
    X = np.array([[1.0, 10.0, 5.0], [2.0, 20.0, 5.0], [3.0, 30.0, 5.0]])
    Z = standardize_columns(X)
    print(Z)
    print("column means:", Z.mean(axis=0))
    print("column stds :", Z.std(axis=0))

    print("\n== outer_op ==")
    a, b = np.array([1, 2, 3]), np.array([10, 20])
    for op in (np.add, np.multiply, np.maximum):
        t = outer_op(a, b, op)
        print(op.__name__, t.tolist(), "loop agrees:", np.array_equal(t, outer_op_loop(a, b, op)))
    print("times table 1..5:\n", outer_op(np.arange(1, 6), np.arange(1, 6), np.multiply), sep="")


if __name__ == "__main__":
    main()
