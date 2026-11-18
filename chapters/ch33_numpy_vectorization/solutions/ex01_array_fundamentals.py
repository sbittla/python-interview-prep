"""
Exercise 01 — Array Fundamentals: dtypes, shapes, creation      [Tier: ★ Core]
Chapter 33 · Pattern: array creation / dtype awareness · Target time: 10 min

Problem
-------
Write three small utilities that an interviewer uses to check you understand what an ndarray is:

1. ``array_info(a)`` returns a dict with ``shape``, ``ndim``, ``size``, ``dtype`` (as a string)
   and ``nbytes`` of the array.
2. ``safe_sum(a)`` sums an integer array without overflow, even when its dtype is tiny
   (``int8``/``uint8``). Return a Python ``int``.
3. ``make_grid(h, w)`` returns an ``(h, w)`` int64 array whose entry ``[i, j] == i * w + j``
   (row-major cell number), built without a Python loop.

Examples
--------
>>> array_info(np.zeros((2, 3), dtype=np.float32))["nbytes"]
24
>>> safe_sum(np.array([100, 100], dtype=np.int8))
200
>>> make_grid(2, 3).tolist()
[[0, 1, 2], [3, 4, 5]]

Constraints
-----------
- 0 <= h, w <= 10_000; empty arrays allowed.

Hints
-----
- ``a.itemsize * a.size == a.nbytes``.
- ``a.sum()`` keeps a small dtype's accumulator for some dtypes on some platforms — pass ``dtype=``.
- ``np.arange(h * w).reshape(h, w)``.

Approach ladder
---------------
1. Brute force — nested Python loops filling a list of lists, O(h*w) Python-level steps.
2. Improved   — ``np.fromfunction`` (still evaluates a vectorised lambda, but allocates index grids).
3. Optimal    — ``np.arange(h*w).reshape(h, w)``: one C-level fill, a reshape is a free view.
   For ``safe_sum`` widen the accumulator: ``a.sum(dtype=np.int64)``.

Follow-ups
----------
- Why does ``np.array([1, 2.5])`` become float64? (upcasting to a common dtype)
- What is the difference between ``np.empty`` and ``np.zeros``? (uninitialised memory)
- How much memory does a (1000, 1000) float32 array take? (4 MB)
"""
from __future__ import annotations

import numpy as np


def array_info(a: np.ndarray) -> dict:
    return {
        "shape": tuple(a.shape),
        "ndim": a.ndim,
        "size": a.size,
        "dtype": str(a.dtype),
        "nbytes": a.nbytes,
    }


def safe_sum(a: np.ndarray) -> int:
    # Widen the accumulator. Unsigned input → uint64, signed → int64.
    acc = np.uint64 if np.issubdtype(a.dtype, np.unsignedinteger) else np.int64
    return int(a.sum(dtype=acc))


def make_grid_loop(h: int, w: int) -> np.ndarray:
    out = np.empty((h, w), dtype=np.int64)
    for i in range(h):
        for j in range(w):
            out[i, j] = i * w + j
    return out


def make_grid(h: int, w: int) -> np.ndarray:
    return np.arange(h * w, dtype=np.int64).reshape(h, w)


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    print("== creation functions ==")
    print("zeros   :", np.zeros(3))
    print("ones int:", np.ones(3, dtype=np.int32))
    print("arange  :", np.arange(0, 10, 3))
    print("linspace:", np.linspace(0, 1, 5))
    print("full    :", np.full((2, 2), 7))
    print("eye     :\n", np.eye(3, dtype=int), sep="")

    print("\n== dtype upcasting ==")
    print("[1, 2.5]      ->", np.array([1, 2.5]).dtype)
    print("[1, True]     ->", np.array([1, True]).dtype)
    print("['a', 1]      ->", np.array(["a", 1]).dtype)
    print("int32 + f32   ->", (np.ones(1, np.int32) + np.ones(1, np.float32)).dtype)

    print("\n== array_info ==")
    for a in [np.zeros((2, 3), dtype=np.float32), np.arange(5), np.empty((0, 4))]:
        print(array_info(a))

    print("\n== overflow and safe_sum ==")
    small = np.array([100, 100, 100], dtype=np.int8)
    print("int8 elementwise 100+100 :", small[:2] + small[1:])  # wraps around
    print("safe_sum(int8)           :", safe_sum(small))
    u = np.full(1000, 255, dtype=np.uint8)
    print("safe_sum(uint8 x1000)    :", safe_sum(u))
    print("astype float -> int truncates:", np.array([1.9, -1.9]).astype(int))

    print("\n== make_grid ==")
    g = make_grid(3, 4)
    print(g)
    print("loop == vectorised:", np.array_equal(g, make_grid_loop(3, 4)))
    print("empty grid shape  :", make_grid(0, 5).shape)


if __name__ == "__main__":
    main()
