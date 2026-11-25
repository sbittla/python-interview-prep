"""
Exercise 04 — Bootstrap Confidence Intervals                     [Tier: ★ Core]
Chapter 35 · Pattern: resampling with replacement · Target time: 20 min

Problem
-------
1. ``bootstrap_ci(x, stat, n_boot=2000, alpha=0.05, seed=0)``: the **percentile**
   bootstrap interval. Draw ``n_boot`` resamples of size n with replacement, apply
   ``stat(sample, axis=-1)`` to each, return the alpha/2 and 1 - alpha/2 quantiles
   (``np.quantile``'s default linear interpolation).
2. ``bootstrap_ci_loop``: the same with a Python loop over resamples, drawing the *same*
   indices, so both must agree exactly.
3. ``normal_ci_mean(x, alpha)``: mean +- z * s / sqrt(n), s with ddof=1 (z from the normal,
   not t: for small n this is slightly too narrow).
4. ``coverage(...)``: fraction of simulated datasets whose interval contains the true mean.

Examples
--------
>>> lo, hi = bootstrap_ci(np.arange(10.0), np.mean, n_boot=500, seed=1)
>>> lo < 4.5 < hi
True

Constraints
-----------
- n >= 2, 0 < alpha < 1; ``stat`` must accept ``axis=-1``.

Approach ladder
---------------
1. Brute force — loop B times: resample, compute the statistic. O(B * n) time, O(n) extra.
2. Optimal    — one (B, n) index matrix and a vectorised statistic along axis 1 (→ §33.4).
   Same O(B * n) work, far less interpreter overhead; O(B * n) memory (chunk if too big).
Also: the normal-approximation interval is O(n) and fine for the mean of a large sample;
the bootstrap earns its cost for medians, ratios, AUC — statistics with no simple SE.

Follow-ups
----------
- Percentile vs basic vs BCa intervals: percentile is simplest; BCa corrects bias and skew.
- The bootstrap resamples *units*: resample users, not page views, when views cluster.
- It fails for extremes (the max) and very small n.
- Edge cases: constant data (zero-width interval), n = 1 (rejected), odd B and quantiles.
"""
from __future__ import annotations

from statistics import NormalDist

import numpy as np


def _check(x: np.ndarray, alpha: float) -> None:
    if x.ndim != 1 or len(x) < 2:
        raise ValueError("need a 1-D sample with at least 2 values")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")


def bootstrap_ci(x, stat=np.mean, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0):
    x = np.asarray(x, dtype=float)
    _check(x, alpha)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))      # row b = indices of resample b
    stats = stat(x[idx], axis=-1)
    lo, hi = np.quantile(stats, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


def bootstrap_ci_loop(x, stat=np.mean, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0):
    x = np.asarray(x, dtype=float)
    _check(x, alpha)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))      # same draws as the fast rung
    stats = [stat(x[row], axis=-1) for row in idx]
    lo, hi = np.quantile(stats, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


def normal_ci_mean(x, alpha: float = 0.05):
    x = np.asarray(x, dtype=float)
    _check(x, alpha)
    z = NormalDist().inv_cdf(1 - alpha / 2)
    half = z * x.std(ddof=1) / np.sqrt(len(x))
    return float(x.mean() - half), float(x.mean() + half)


def coverage(method: str, n: int, reps: int = 300, seed: int = 0, n_boot: int = 1000) -> float:
    """Exponential(1) data, true mean 1: how often does the 95 % interval contain it?"""
    rng = np.random.default_rng(seed)
    hits = 0
    for r in range(reps):
        x = rng.exponential(1.0, size=n)
        lo, hi = bootstrap_ci(x, np.mean, n_boot, seed=r) if method == "bootstrap" else normal_ci_mean(x)
        hits += lo <= 1.0 <= hi
    return hits / reps


def main() -> None:
    rng = np.random.default_rng(35)
    x = rng.exponential(scale=2.0, size=40)          # skewed: mean 2, median 2 ln 2 ~ 1.386
    print("sample mean, median:", round(x.mean(), 3), round(float(np.median(x)), 3))
    fast = bootstrap_ci(x, np.mean, seed=7)
    slow = bootstrap_ci_loop(x, np.mean, seed=7)
    print("bootstrap 95% CI mean  :", tuple(round(v, 3) for v in fast), " loop agrees:", fast == slow)
    print("normal    95% CI mean  :", tuple(round(v, 3) for v in normal_ci_mean(x)))
    print("bootstrap 95% CI median:", tuple(round(v, 3) for v in bootstrap_ci(x, np.median, seed=7)))
    print("constant data CI       :", bootstrap_ci(np.full(5, 3.0), np.mean))
    for n in (10, 100):
        print(f"coverage n={n:<3} bootstrap={coverage('bootstrap', n):.2f}  normal={coverage('normal', n):.2f}  (target 0.95)")


if __name__ == "__main__":
    main()
