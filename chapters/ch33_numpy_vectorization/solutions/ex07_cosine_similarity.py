"""
Exercise 07 — Cosine Similarity and Top-k Retrieval              [Tier: ★ Core]
Chapter 33 · Pattern: row normalisation + matmul · Target time: 15 min

Problem
-------
1. ``cosine_similarity_matrix(A, B)`` returns the (m, n) matrix of cosine similarities between the
   rows of A and the rows of B. A zero vector has similarity 0 with everything (no NaN).
2. ``top_k_similar(query, corpus, k)`` returns ``(indices, scores)`` of the k corpus rows most
   similar to the 1-D ``query``, best first (ties → lower index first).

Examples
--------
>>> cosine_similarity_matrix(np.array([[1., 0.]]), np.array([[2., 0.], [0., 3.], [-1., 0.]])).tolist()
[[1.0, 0.0, -1.0]]

Constraints
-----------
- Similarities lie in [-1, 1] (clip floating-point overshoot).

Hints
-----
- cos(a, b) = a·b / (||a|| ||b||). Normalise rows once, then one matmul gives every pair.
- ``np.linalg.norm(A, axis=1, keepdims=True)``; replace zero norms by 1 before dividing.

Approach ladder
---------------
1. Brute force — double loop computing a·b / (|a||b|) per pair: O(mnd), recomputes norms m*n times.
2. Improved   — precompute norms, loop over pairs: still Python-level O(mn).
3. Optimal    — L2-normalise rows, ``A_hat @ B_hat.T``: O(mnd) in BLAS. Top-k with argpartition.

Follow-ups
----------
- Cosine vs Euclidean on normalised vectors: ||a-b||^2 = 2 - 2cos(a,b), so rankings agree.
- Why do embedding systems store vectors pre-normalised? (dot product == cosine)
"""
from __future__ import annotations

import numpy as np


def _normalize_rows(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=float)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(norms == 0, 1.0, norms)


def cosine_loop(A, B):
    out = np.zeros((len(A), len(B)))
    for i, a in enumerate(A):
        for j, b in enumerate(B):
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            out[i, j] = 0.0 if na == 0 or nb == 0 else a @ b / (na * nb)
    return out


def cosine_similarity_matrix(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    S = _normalize_rows(A) @ _normalize_rows(B).T
    return np.clip(S, -1.0, 1.0)


def top_k_similar(query: np.ndarray, corpus: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    scores = cosine_similarity_matrix(np.asarray(query)[None, :], corpus)[0]
    k = min(k, scores.size)
    order = np.lexsort((np.arange(scores.size), -scores))[:k]
    return order, scores[order]


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    A = np.array([[1.0, 0.0], [1.0, 1.0], [0.0, 0.0]])
    B = np.array([[2.0, 0.0], [0.0, 3.0], [-1.0, 0.0]])
    S = cosine_similarity_matrix(A, B)
    print("S =\n", S, sep="")
    print("loop agrees:", np.allclose(S, cosine_loop(A, B)))
    print("zero-vector row is all 0:", np.all(S[2] == 0))

    print("\n== tiny retrieval demo ==")
    vocab = ["cat", "dog", "pet", "car", "road"]
    # hand-made 4-d "embeddings": [animal, vehicle, fluffy, outdoor]
    E = np.array([[0.9, 0.0, 0.8, 0.1],
                  [0.8, 0.0, 0.6, 0.4],
                  [0.7, 0.0, 0.9, 0.0],
                  [0.0, 0.9, 0.0, 0.5],
                  [0.0, 0.6, 0.0, 0.9]])
    q = np.array([1.0, 0.0, 0.7, 0.2])
    idx, sc = top_k_similar(q, E, 3)
    for i, s in zip(idx, sc):
        print(f"  {vocab[i]:<5} {s:.4f}")

    print("\n== cosine vs euclidean on unit vectors ==")
    rng = np.random.default_rng(1)
    X = _normalize_rows(rng.normal(size=(6, 8)))
    cos = X @ X.T
    sq = ((X[:, None] - X[None]) ** 2).sum(-1)
    print("||a-b||^2 == 2 - 2cos:", np.allclose(sq, 2 - 2 * cos))
    print("same nearest neighbour ranking:",
          np.array_equal(np.argsort(-cos[0])[1:], np.argsort(sq[0])[1:]))


if __name__ == "__main__":
    main()
