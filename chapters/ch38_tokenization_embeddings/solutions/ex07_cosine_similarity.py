"""
Exercise 07 — Cosine Similarity, Dot Product and Normalisation    [Tier: ★ Core]
Chapter 38 · Pattern: vectorised similarity · Target time: 15 min

Problem
-------
Implement, with NumPy and without Python loops over rows:

- ``cosine(a, b)``: ``a·b / (|a| |b|)``; return ``0.0`` if either vector is all zeros.
- ``l2_normalize(X, eps)``: divide each row by its L2 norm (rows with norm < eps stay 0).
- ``pairwise_cosine(A, B)``: an ``(n, m)`` matrix of cosines between rows of A and B.
- ``euclid_from_cosine(c)``: for *unit* vectors, ``|a - b|^2 = 2 - 2 cos(a, b)``.

Then show that ranking by raw dot product and by cosine can disagree when vector norms
differ, and that after normalisation they agree.

Examples
--------
>>> cosine(np.array([1.0, 0.0]), np.array([1.0, 1.0]))
0.7071067811865475
>>> cosine(np.zeros(2), np.ones(2))
0.0

Constraints
-----------
- No division-by-zero warnings for zero rows.

Hints
-----
- ``np.linalg.norm(X, axis=1, keepdims=True)`` keeps the shape broadcastable.
- ``l2_normalize(A) @ l2_normalize(B).T`` is the whole pairwise matrix.

Approach ladder
---------------
1. Brute force — double loop calling ``cosine`` for each pair: O(n·m·d) with Python
   overhead per pair.
2. Optimal    — normalise once (O((n+m)·d)), then one matrix multiply (O(n·m·d) in BLAS).
   Vector databases store normalised vectors so that cosine == dot product.

Follow-ups
----------
- When is dot product preferable to cosine? (When magnitude carries signal, e.g. models
  trained with a dot-product objective, or popularity encoded in the norm.)
- Why is |a-b| ranking identical to cosine ranking for unit vectors?
"""
from __future__ import annotations

import numpy as np


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(a @ b / (na * nb))


def l2_normalize(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    norms = np.linalg.norm(X, axis=-1, keepdims=True)
    safe = np.where(norms < eps, 1.0, norms)
    return np.where(norms < eps, 0.0, X / safe)


def pairwise_cosine(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return l2_normalize(A) @ l2_normalize(B).T


def pairwise_cosine_loops(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return np.array([[cosine(a, b) for b in B] for a in A])


def euclid_from_cosine(c: np.ndarray) -> np.ndarray:
    return np.sqrt(np.maximum(2.0 - 2.0 * np.asarray(c), 0.0))


def main() -> None:
    print(f"cosine([1,0],[1,1]) = {cosine(np.array([1.0, 0.0]), np.array([1.0, 1.0])):.4f}")
    print(f"cosine(zeros, ones) = {cosine(np.zeros(2), np.ones(2))}")

    query = np.array([1.0, 1.0])
    docs = {"short-aligned": np.array([1.0, 1.0]),
            "long-off-axis": np.array([5.0, 0.5]),
            "tiny-aligned": np.array([0.1, 0.1])}
    names = list(docs)
    D = np.stack([docs[n] for n in names])
    dots = D @ query
    coss = pairwise_cosine(D, query[None, :])[:, 0]
    print("\n doc            dot     cosine")
    for n, d, c in zip(names, dots, coss):
        print(f" {n:14s} {d:6.2f}  {c:6.3f}")
    print(f"rank by dot:    {[names[i] for i in np.argsort(-dots, kind='stable')]}")
    print(f"rank by cosine: {[names[i] for i in np.argsort(-coss, kind='stable')]}")
    Dn = l2_normalize(D)
    print(f"after normalising rows, dot == cosine: {np.allclose(Dn @ l2_normalize(query), coss)}")

    rng = np.random.default_rng(0)
    A, B = rng.normal(size=(50, 32)), rng.normal(size=(40, 32))
    A[3] = 0.0
    P = pairwise_cosine(A, B)
    print(f"\npairwise shape: {P.shape}  matches loops: {np.allclose(P, pairwise_cosine_loops(A, B))}")
    print(f"zero row gives zeros: {bool(np.all(P[3] == 0))}  range ok: {bool(P.min() >= -1 and P.max() <= 1)}")
    An, Bn = l2_normalize(A[:5]), l2_normalize(B[:5])
    direct = np.linalg.norm(An[:, None, :] - Bn[None, :, :], axis=-1)
    print(f"|a-b| = sqrt(2-2cos) for unit vectors: {np.allclose(direct, euclid_from_cosine(An @ Bn.T))}")


if __name__ == "__main__":
    main()
