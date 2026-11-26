"""
Exercise 06 — Approximate Nearest Neighbours with an IVF Index     [Tier: ◆ Extended]
Chapter 40 · Pattern: coarse clustering + probe the nearest lists · Target time: 40 min

Problem
-------
Vectors are unit length, similarity is the dot product (= cosine).

1. ``exact_top_k(X, q, k)``: brute-force row indices of the k most similar rows
   (ties -> smaller index).
2. ``spherical_kmeans(X, nlist, iters, seed)``: initial centroids are ``nlist`` distinct rows
   chosen with ``np.random.default_rng(seed)``; assign each row to its most similar centroid
   (ties -> smaller centroid index); new centroid = normalised mean of its rows; an empty
   cluster keeps its old centroid. Returns ``(centroids, assignment)``.
3. ``IVFIndex(X, nlist, iters=10, seed=0)``: an inverted file — one list of row ids per
   centroid. ``search(q, k, nprobe)`` scores the ``nprobe`` most similar centroids, scans only
   their lists exactly, and returns ``(top-k row ids, number of vectors scanned)``.
4. ``recall_at_k(approx, exact)`` = |approx ∩ exact| / |exact|  (→ §35.9).

Examples
--------
>>> X = np.eye(3)
>>> exact_top_k(X, np.array([0.0, 1.0, 0.0]), 2)
[1, 0]

Constraints
-----------
- 1 <= nprobe <= nlist <= N. With nprobe == nlist the search is exact.

Approach ladder
---------------
1. Brute force — score all N vectors: O(N d) per query, recall 1.0.
2. IVF        — O(nlist · d) to rank centroids + O(nprobe · N/nlist · d) to scan the probed
   lists (for balanced lists). Build: k-means, O(iters · N · nlist · d).
   nprobe is the recall-vs-work knob: more lists scanned, higher recall.
3. Further    — product quantisation (PQ) compresses each vector to m one-byte codes so the
   scanned lists fit in memory (IVF-PQ); graph indexes (HNSW) walk a proximity graph instead
   of scanning lists. Both trade exactness for speed or memory, so measure recall@k against
   brute force on a sample of real queries — never assume it.
   Why move up: at 10^8 vectors × 768 float32 dims (≈ 307 GB), brute force is too slow and
   too big.

Follow-ups
----------
- Why can a true neighbour be missed? It sits in a list whose centroid is not among the
  nprobe nearest (queries near cluster boundaries).
- nlist is usually chosen on the order of sqrt(N) (or a small multiple of it); tune nprobe on
  held-out queries for a target recall@k.
- Inserts go to the nearest list; if the data drifts, the centroids go stale -> rebuild.
"""
from __future__ import annotations

import numpy as np


def _normalise(X: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return np.divide(X, n, out=np.zeros_like(X), where=n > 0)


def _top_rows(scores: np.ndarray, rows: np.ndarray, k: int) -> list[int]:
    order = np.lexsort((rows, -np.round(scores, 9)))     # last key is primary: score desc, then row
    return rows[order[:k]].tolist()


def exact_top_k(X: np.ndarray, q: np.ndarray, k: int) -> list[int]:
    return _top_rows(X @ q, np.arange(len(X)), k)


def spherical_kmeans(X: np.ndarray, nlist: int, iters: int = 10,
                     seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    C = X[rng.choice(len(X), size=nlist, replace=False)].copy()
    assign = np.zeros(len(X), dtype=int)
    for _ in range(iters):
        assign = np.argmax(X @ C.T, axis=1)               # argmax returns the first max: ties -> smaller index
        for c in range(nlist):
            members = X[assign == c]
            if len(members):
                C[c] = members.mean(axis=0)
        C = _normalise(C)
    return C, np.argmax(X @ C.T, axis=1)


class IVFIndex:
    def __init__(self, X: np.ndarray, nlist: int, iters: int = 10, seed: int = 0) -> None:
        self.X = X
        self.centroids, assign = spherical_kmeans(X, nlist, iters, seed)
        self.lists = [np.flatnonzero(assign == c) for c in range(nlist)]

    def search(self, q: np.ndarray, k: int, nprobe: int) -> tuple[list[int], int]:
        probe = _top_rows(self.centroids @ q, np.arange(len(self.centroids)), nprobe)
        cand = np.concatenate([self.lists[c] for c in probe])
        return _top_rows(self.X[cand] @ q, cand, k), len(cand)


def recall_at_k(approx: list[int], exact: list[int]) -> float:
    return len(set(approx) & set(exact)) / len(exact) if exact else 1.0


def make_data(n: int = 4000, d: int = 32, clusters: int = 40, n_queries: int = 100,
              seed: int = 40) -> tuple[np.ndarray, np.ndarray]:
    """Clustered unit vectors (embeddings of real text are clustered by topic, too)."""
    rng = np.random.default_rng(seed)
    centres = rng.normal(size=(clusters, d))
    pts = centres[rng.integers(0, clusters, n + n_queries)] + 1.5 * rng.normal(size=(n + n_queries, d))
    pts = _normalise(pts)
    return pts[:n], pts[n:]


def main() -> None:
    print("toy exact_top_k:", exact_top_k(np.eye(3), np.array([0.0, 1.0, 0.0]), 2))
    X, Q = make_data()
    k, nlist = 10, 64
    index = IVFIndex(X, nlist)
    sizes = sorted(len(lst) for lst in index.lists)
    print(f"N={len(X)} d={X.shape[1]} nlist={nlist}: list sizes min={sizes[0]} "
          f"median={sizes[len(sizes) // 2]} max={sizes[-1]}")
    exact = [exact_top_k(X, q, k) for q in Q]
    print(f"{'nprobe':>6} {'recall@10':>9} {'scanned/N':>9}")
    for nprobe in (1, 2, 4, 8, 16, 32, 64):
        rec = scanned = 0.0
        for q, ex in zip(Q, exact):
            got, n_scanned = index.search(q, k, nprobe)
            rec += recall_at_k(got, ex)
            scanned += n_scanned
        print(f"{nprobe:>6} {rec / len(Q):>9.3f} {scanned / len(Q) / len(X):>9.3f}")


if __name__ == "__main__":
    main()
