"""
Exercise 14 — Random Numbers, Seeding and Reproducible Splits    [Tier: ★ Core]
Chapter 33 · Pattern: Generator API / permutation-based sampling · Target time: 15 min

Problem
-------
1. ``train_test_indices(n, test_frac, seed)``: return ``(train_idx, test_idx)`` — a reproducible
   random split of ``range(n)`` with ``round(n * test_frac)`` test items, both sorted, disjoint,
   covering everything.
2. ``bootstrap_means(x, n_boot, seed)``: ``n_boot`` bootstrap resample means of ``x`` computed in
   one vectorised draw (no Python loop over resamples).
3. ``independent_streams(seed, k)``: ``k`` statistically independent ``Generator`` objects
   (e.g. one per worker) derived from one seed.

Examples
--------
>>> tr, te = train_test_indices(10, 0.3, seed=0); len(te), len(set(tr) | set(te))
(3, 10)

Constraints
-----------
- Same seed ⇒ identical output on every run and machine (same NumPy major version).

Hints
-----
- ``rng = np.random.default_rng(seed)``; ``rng.permutation(n)``.
- ``rng.integers(0, n, size=(n_boot, n))`` draws all resample indices at once.
- ``np.random.SeedSequence(seed).spawn(k)``.

Approach ladder
---------------
1. Brute force — ``random.sample`` / global ``np.random.seed``: hidden global state, any other
   library call that draws numbers changes your split.
2. Improved   — local ``Generator`` with a loop of ``rng.choice`` per bootstrap sample.
3. Optimal    — local ``Generator`` + one (n_boot, n) index draw, ``x[idx].mean(axis=1)``.
   For parallel work use ``SeedSequence.spawn`` instead of ``seed + i``.

Follow-ups
----------
- Why prefer ``default_rng`` over the legacy ``np.random.rand``? (explicit state, better PCG64)
- Memory of the vectorised bootstrap is O(n_boot * n): chunk it if that is too large.
"""
from __future__ import annotations

import numpy as np


def train_test_indices(n: int, test_frac: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    n_test = int(round(n * test_frac))
    return np.sort(perm[n_test:]), np.sort(perm[:n_test])


def bootstrap_means_loop(x, n_boot, seed):
    rng = np.random.default_rng(seed)
    return np.array([rng.choice(x, size=len(x), replace=True).mean() for _ in range(n_boot)])


def bootstrap_means(x: np.ndarray, n_boot: int, seed: int) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, x.size, size=(n_boot, x.size))
    return x[idx].mean(axis=1)


def independent_streams(seed: int, k: int) -> list[np.random.Generator]:
    return [np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(k)]


def main() -> None:
    np.set_printoptions(precision=4, suppress=True)
    rng = np.random.default_rng(2024)
    print("uniform   :", rng.random(3))
    print("normal    :", rng.normal(0, 1, size=3))
    print("integers  :", rng.integers(0, 10, size=5), "(high is exclusive)")
    print("choice    :", rng.choice(["a", "b", "c"], size=4, p=[0.5, 0.25, 0.25]))
    print("shuffle-free permutation:", rng.permutation(6))

    print("\n== reproducibility ==")
    a = np.random.default_rng(7).normal(size=3)
    b = np.random.default_rng(7).normal(size=3)
    print("same seed same numbers:", np.array_equal(a, b))

    print("\n== train/test split ==")
    tr, te = train_test_indices(10, 0.3, seed=0)
    print("train:", tr, " test:", te)
    print("disjoint & complete:", set(tr).isdisjoint(te) and len(tr) + len(te) == 10)
    print("reproducible:", np.array_equal(te, train_test_indices(10, 0.3, seed=0)[1]))

    print("\n== bootstrap ==")
    x = np.random.default_rng(1).exponential(2.0, size=200)
    bm = bootstrap_means(x, 2_000, seed=42)
    print("sample mean          :", round(float(x.mean()), 4))
    print("bootstrap mean of means:", round(float(bm.mean()), 4))
    print("bootstrap std (SE)   :", round(float(bm.std()), 4),
          " analytic s/sqrt(n):", round(float(x.std(ddof=1) / np.sqrt(x.size)), 4))
    lo, hi = np.percentile(bm, [2.5, 97.5])
    print(f"95% percentile CI    : [{lo:.4f}, {hi:.4f}]")
    loop = bootstrap_means_loop(x, 2_000, seed=42)
    print("loop version SE close:", abs(loop.std() - bm.std()) < 0.02)

    print("\n== independent streams ==")
    streams = independent_streams(99, 3)
    for i, g in enumerate(streams):
        print(f"worker {i}:", g.integers(0, 100, size=4))


if __name__ == "__main__":
    main()
