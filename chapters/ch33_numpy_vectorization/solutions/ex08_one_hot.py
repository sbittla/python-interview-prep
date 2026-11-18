"""
Exercise 08 — One-Hot Encoding and Back                          [Tier: ★ Core]
Chapter 33 · Pattern: fancy-index assignment · Target time: 10 min

Problem
-------
1. ``one_hot(labels, num_classes)``: integer labels of shape (n,) → float array (n, num_classes)
   with a single 1 per row. Raise ``ValueError`` for labels outside [0, num_classes).
2. ``from_one_hot(Y)``: inverse — argmax per row.
3. ``encode_categories(values)``: map arbitrary hashable category values (e.g. strings) to
   ``(codes, categories)`` where ``categories`` is the sorted unique array and
   ``categories[codes] == values``.

Examples
--------
>>> one_hot(np.array([2, 0]), 3).tolist()
[[0.0, 0.0, 1.0], [1.0, 0.0, 0.0]]
>>> encode_categories(np.array(["b", "a", "b"]))[0].tolist()
[1, 0, 1]

Constraints
-----------
- n up to 10^6; num_classes up to 10^4 (output is dense — mind the memory).

Hints
-----
- ``Y[np.arange(n), labels] = 1`` sets one cell per row.
- ``np.eye(num_classes)[labels]`` is a cute one-liner (but builds a k x k identity first).
- ``np.unique(values, return_inverse=True)``.

Approach ladder
---------------
1. Brute force — loop setting ``Y[i, labels[i]] = 1``: O(n) Python steps.
2. Improved   — ``np.eye(k)[labels]``: vectorised, but allocates a k x k identity (bad for big k).
3. Optimal    — allocate zeros (n, k) once and fancy-assign: O(nk) memory for output only.

Follow-ups
----------
- When is one-hot a bad idea? (high cardinality → embeddings, hashing, target encoding)
- How do you one-hot in a deep-learning loss? (you usually don't: pass class indices)
"""
from __future__ import annotations

import numpy as np


def one_hot_loop(labels, num_classes):
    Y = np.zeros((len(labels), num_classes))
    for i, c in enumerate(labels):
        Y[i, c] = 1.0
    return Y


def one_hot(labels: np.ndarray, num_classes: int) -> np.ndarray:
    labels = np.asarray(labels, dtype=np.int64)
    if labels.size and (labels.min() < 0 or labels.max() >= num_classes):
        raise ValueError("label out of range")
    Y = np.zeros((labels.size, num_classes))
    Y[np.arange(labels.size), labels] = 1.0
    return Y


def from_one_hot(Y: np.ndarray) -> np.ndarray:
    return np.asarray(Y).argmax(axis=1)


def encode_categories(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    categories, codes = np.unique(np.asarray(values), return_inverse=True)
    return codes.reshape(-1), categories


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    labels = np.array([2, 0, 1, 2])
    Y = one_hot(labels, 3)
    print("one_hot =\n", Y, sep="")
    print("loop agrees   :", np.array_equal(Y, one_hot_loop(labels, 3)))
    print("np.eye agrees :", np.array_equal(Y, np.eye(3)[labels]))
    print("round trip    :", from_one_hot(Y))
    print("empty         :", one_hot(np.array([], dtype=int), 4).shape)
    try:
        one_hot(np.array([0, 3]), 3)
    except ValueError as e:
        print("bad label     : ValueError:", e)

    print("\n== categorical strings ==")
    colors = np.array(["red", "green", "red", "blue", "green"])
    codes, cats = encode_categories(colors)
    print("categories:", cats)
    print("codes     :", codes)
    print("decoded ok:", np.array_equal(cats[codes], colors))
    print("one-hot   :\n", one_hot(codes, len(cats)), sep="")


if __name__ == "__main__":
    main()
