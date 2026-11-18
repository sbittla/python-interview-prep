"""
Exercise 05 — k-Means with Random and k-means++ Initialisation        [Tier: ★ Core]
Chapter 36 · Pattern: alternating optimisation (Lloyd's algorithm) · Target time: 30 min

Problem
-------
Implement Lloyd's k-means:

- ``init_random(X, k, rng)`` — k distinct data points chosen uniformly;
- ``init_kmeans_pp(X, k, rng)`` — k-means++: first centre uniform, each next centre sampled with
  probability proportional to D(x)², the squared distance to the nearest chosen centre;
- ``kmeans(X, k, init, seed, max_iter, tol)`` returning (centroids, labels, inertia, n_iter),
  where inertia = Σ‖xᵢ − μ_{c(i)}‖². An empty cluster is re-seeded at the point farthest from
  its current centroid.

Examples
--------
>>> X = np.array([[0.0, 0.0], [0.0, 1.0], [10.0, 0.0], [10.0, 1.0]])
>>> c, labels, inertia, _ = kmeans(X, 2, init="k-means++", seed=0)
>>> round(inertia, 4)
1.0

Constraints
-----------
- NumPy only; all randomness from ``np.random.default_rng(seed)``.

Approach ladder
---------------
1. Naive — random init, single run: each iteration O(n·k·d), but it often converges to a poor
   local minimum (two centres in one blob, one centre covering two blobs).
2. Better — several random restarts, keep the lowest inertia (sklearn's n_init).
3. k-means++ — O(n·k·d) seeding that is O(log k)-competitive in expectation with the optimum;
   in practice fewer iterations and lower inertia from a single run.

Hints
-----
- Assignment step: argmin over the (n, k) squared-distance matrix.
- Update step: mean of the points assigned to each centre.
- Stop when centres move less than tol (or labels stop changing).

Follow-ups
----------
- How do you choose k? (Elbow on inertia, silhouette score, or the downstream task.)
- Why does k-means struggle with elongated or differently-sized clusters? (It implicitly assumes
  spherical, equal-variance clusters — a GMM relaxes this.)
- Mini-batch k-means for large n.
"""
from __future__ import annotations

import numpy as np

TRUE_CENTERS = np.array([[5.0 * i, 5.0 * j] for i in range(3) for j in range(3)])  # 3x3 grid
SIZES = [20, 40, 60] * 3                                                              # uneven blobs


def make_data(seed: int = 0):
    rng = np.random.default_rng(seed)
    X = np.vstack([rng.normal(c, 0.7, size=(s, 2)) for c, s in zip(TRUE_CENTERS, SIZES)])
    return X[rng.permutation(len(X))]


def _sq_dists(X: np.ndarray, C: np.ndarray) -> np.ndarray:
    return ((X[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)


def init_random(X: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    idx = rng.choice(len(X), size=k, replace=False)
    return X[idx].copy()


def init_kmeans_pp(X: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    centers = [X[rng.integers(len(X))]]
    d2 = ((X - centers[0]) ** 2).sum(axis=1)
    for _ in range(1, k):
        probs = d2 / d2.sum()
        nxt = X[rng.choice(len(X), p=probs)]
        centers.append(nxt)
        d2 = np.minimum(d2, ((X - nxt) ** 2).sum(axis=1))
    return np.array(centers)


def kmeans(X: np.ndarray, k: int, init: str = "k-means++", seed: int = 0,
           max_iter: int = 100, tol: float = 1e-6):
    rng = np.random.default_rng(seed)
    C = init_kmeans_pp(X, k, rng) if init == "k-means++" else init_random(X, k, rng)
    labels = np.zeros(len(X), dtype=int)
    n_iter = 0
    for n_iter in range(1, max_iter + 1):
        D = _sq_dists(X, C)
        labels = D.argmin(axis=1)
        new_C = C.copy()
        for j in range(k):
            members = X[labels == j]
            if len(members):
                new_C[j] = members.mean(axis=0)
            else:                                   # empty cluster: re-seed at farthest point
                far = int(D[np.arange(len(X)), labels].argmax())
                new_C[j] = X[far]
        shift = np.sqrt(((new_C - C) ** 2).sum(axis=1)).max()
        C = new_C
        if shift < tol:
            break
    D = _sq_dists(X, C)
    labels = D.argmin(axis=1)
    inertia = float(D[np.arange(len(X)), labels].sum())
    return C, labels, inertia, n_iter


def main() -> None:
    X_toy = np.array([[0.0, 0.0], [0.0, 1.0], [10.0, 0.0], [10.0, 1.0]])
    _, lab, inertia, _ = kmeans(X_toy, 2, seed=0)
    print("toy labels:", lab.tolist(), "inertia:", round(inertia, 4))

    X = make_data()
    print("seed | random: inertia iters | k-means++: inertia iters")
    rand_inertias, pp_inertias = [], []
    for seed in range(10):
        _, _, ir, nr = kmeans(X, 9, init="random", seed=seed)
        _, _, ip, npp = kmeans(X, 9, init="k-means++", seed=seed)
        rand_inertias.append(ir)
        pp_inertias.append(ip)
        print(f"  {seed}  | {ir:10.4f} {nr:3d}         | {ip:10.4f} {npp:3d}")
    print(f"mean inertia random={np.mean(rand_inertias):.4f}  k-means++={np.mean(pp_inertias):.4f}")
    print(f"best of 10 random restarts={min(rand_inertias):.4f}  best of 10 k-means++={min(pp_inertias):.4f}")

    best_seed = int(np.argmin(pp_inertias))
    C, _, _, _ = kmeans(X, 9, seed=best_seed)
    order = np.lexsort((C[:, 1], C[:, 0]))
    print("k-means++ centroids (sorted):", np.round(C[order], 4).tolist())

    print("elbow (best of 5 k-means++ runs per k):")
    for k in range(1, 13):
        print(f"  k={k} inertia={min(kmeans(X, k, seed=s)[2] for s in range(5)):.4f}")


if __name__ == "__main__":
    main()
