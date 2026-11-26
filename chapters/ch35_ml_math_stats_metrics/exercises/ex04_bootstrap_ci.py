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

Hints
-----
- ``rng.integers(0, n, size=(B, n))`` gives all resample indices at once; ``x[idx]`` is (B, n).
- Apply the statistic along axis 1 (``stat(..., axis=-1)``), then take two quantiles.
- The loop rung must draw the same index matrix so the two rungs agree exactly.
- Normal interval: ``statistics.NormalDist().inv_cdf(1 - alpha / 2)`` and ``std(ddof=1)``.

Wrong-but-tempting
------------------
- Resampling without replacement: every resample is a permutation, the spread is zero.
- Resample size != n: changes the variance you are estimating.
- Reading the interval as "95 % probability the true mean is in this interval".

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
    raise NotImplementedError("TODO")


def bootstrap_ci_loop(x, stat=np.mean, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0):
    raise NotImplementedError("TODO")


def normal_ci_mean(x, alpha: float = 0.05):
    raise NotImplementedError("TODO")


def coverage(method: str, n: int, reps: int = 300, seed: int = 0, n_boot: int = 1000) -> float:
    """Exponential(1) data, true mean 1: how often does the 95 % interval contain it?"""
    raise NotImplementedError("TODO")


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
        print(f"coverage n={n:<3} bootstrap={coverage('bootstrap', n, reps=2000):.3f}  normal={coverage('normal', n, reps=2000):.3f}  (target 0.95, 2000 datasets)")


if __name__ == "__main__":
    main()
