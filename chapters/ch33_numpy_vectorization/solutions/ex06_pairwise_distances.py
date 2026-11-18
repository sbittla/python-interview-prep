"""
Exercise 06 — Pairwise Euclidean Distance Matrix                 [Tier: ★ Core]
Chapter 33 · Pattern: broadcasting / Gram-matrix trick · Target time: 20 min

Problem
-------
Given ``A`` with shape (m, d) and ``B`` with shape (n, d), return the (m, n) matrix ``D`` with
``D[i, j] = ||A[i] - B[j]||_2``. Implement three versions and show they agree:

- ``pairwise_loop``       — double loop (reference)
- ``pairwise_broadcast``  — (m, 1, d) - (1, n, d) broadcasting
- ``pairwise_gram``       — ||a||^2 + ||b||^2 - 2 a.b using one matrix product

Then use it: ``nearest_neighbor(A, B)`` returns, for each row of A, the index of the closest row of B.

Examples
--------
>>> pairwise_gram(np.array([[0., 0.]]), np.array([[3., 4.], [0., 1.]])).tolist()
[[5.0, 1.0]]

Constraints
-----------
- m, n up to a few thousand, d up to a few hundred. Distances must be non-negative and the
  diagonal of D(A, A) must be exactly 0.

Hints
-----
- ``A[:, None, :] - B[None, :, :]`` has shape (m, n, d) — memory O(mnd)!
- ``(A**2).sum(1)[:, None] + (B**2).sum(1)[None, :] - 2 * A @ B.T``.
- Floating-point cancellation can make squared distances slightly negative: clip at 0.

Approach ladder
---------------
1. Brute force — double Python loop: O(mnd) time, slow constant.
2. Improved   — 3-D broadcasting: O(mnd) time in C but O(mnd) *memory* for the temporary.
3. Optimal    — Gram trick: one BLAS matmul O(mnd) time, O(mn) memory; clip negatives, fix the
   diagonal for self-distances. Why move up: the broadcast temp blows memory at (5000, 5000, 512).

Follow-ups
----------
- How would you do it for 10^6 x 10^6? (chunk rows; or approximate nearest neighbour indexes)
- When is the Gram trick numerically worse? (points far from origin, tiny distances: centre first)
"""
from __future__ import annotations

import numpy as np


def pairwise_loop(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    D = np.empty((len(A), len(B)))
    for i in range(len(A)):
        for j in range(len(B)):
            D[i, j] = np.sqrt(((A[i] - B[j]) ** 2).sum())
    return D


def pairwise_broadcast(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    diff = A[:, None, :] - B[None, :, :]       # (m, n, d)
    return np.sqrt((diff ** 2).sum(axis=-1))


def pairwise_gram(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    sq = (A ** 2).sum(1)[:, None] + (B ** 2).sum(1)[None, :] - 2.0 * (A @ B.T)
    np.maximum(sq, 0.0, out=sq)                # kill tiny negatives from cancellation
    return np.sqrt(sq)


def self_distances(A: np.ndarray) -> np.ndarray:
    D = pairwise_gram(A, A)
    np.fill_diagonal(D, 0.0)
    return D


def nearest_neighbor(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return pairwise_gram(A, B).argmin(axis=1)


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    rng = np.random.default_rng(0)
    A = rng.normal(size=(4, 3))
    B = rng.normal(size=(5, 3))
    D1, D2, D3 = pairwise_loop(A, B), pairwise_broadcast(A, B), pairwise_gram(A, B)
    print("D (4x5) =\n", D3, sep="")
    print("broadcast == loop:", np.allclose(D1, D2))
    print("gram      == loop:", np.allclose(D1, D3))

    print("\n== numerical cancellation ==")
    far = rng.normal(size=(3, 2)) + 1e8      # points far from the origin
    raw = (far ** 2).sum(1)[:, None] + (far ** 2).sum(1)[None, :] - 2 * far @ far.T
    print("raw squared self-distance diagonal has non-zero/negative values:",
          bool(np.any(np.diag(raw) != 0)))
    centred = far - far.mean(axis=0)
    print("after centring, gram == broadcast:",
          np.allclose(pairwise_gram(centred, centred), pairwise_broadcast(far, far)))
    print("self_distances diagonal:", np.diag(self_distances(A)))

    print("\n== nearest neighbour ==")
    queries = np.array([[0.0, 0.0], [5.0, 5.0], [-3.0, 1.0]])
    points = np.array([[1.0, 1.0], [4.0, 4.0], [-2.0, 0.0], [10.0, 10.0]])
    print("nearest index:", nearest_neighbor(queries, points))
    print("distances    :\n", pairwise_gram(queries, points), sep="")

    print("\n== memory of the broadcast temporary ==")
    m, n, d = 5000, 5000, 512
    print(f"(m, n, d) float64 temp = {m * n * d * 8 / 1e9:.1f} GB ; gram result = {m * n * 8 / 1e6:.0f} MB")


if __name__ == "__main__":
    main()
