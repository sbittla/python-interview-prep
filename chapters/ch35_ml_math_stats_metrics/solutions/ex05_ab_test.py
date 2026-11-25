"""
Exercise 05 — A/B Test: Two-Proportion z-Test, Power, Peeking    [Tier: ★ Core]
Chapter 35 · Pattern: hypothesis testing · Target time: 25 min

Problem
-------
Control A converted x_a of n_a users; treatment B converted x_b of n_b.

1. ``two_proportion_ztest(x_a, n_a, x_b, n_b, alternative="two-sided")`` -> (z, p).
   H0: p_a == p_b. Pooled rate p = (x_a + x_b) / (n_a + n_b);
   SE = sqrt(p (1 - p) (1/n_a + 1/n_b)); z = (p_b - p_a) / SE.
   two-sided p = P(|Z| >= |z|) = erfc(|z| / sqrt 2); "larger" (B > A) p = P(Z >= z).
   Raise ``ValueError`` if SE == 0 (both arms all 0 or all 1).
2. ``diff_ci(...)``: Wald interval for p_b - p_a with the *unpooled* SE.
3. ``permutation_pvalue(...)``: brute-force two-sided test by shuffling arm labels;
   p = (1 + #{|diff*| >= |diff|}) / (1 + n_perm).
4. ``sample_size_per_arm(p1, p2, alpha=0.05, power=0.8)``: two-sided, equal arms.
5. ``peeking_false_positive_rate(...)``: A/A simulation that stops at the first of k looks
   with p < alpha. Shows why "stop when significant" inflates false positives.

Examples
--------
>>> z, p = two_proportion_ztest(200, 2000, 250, 2000)
>>> round(z, 3), round(p, 4)
(2.502, 0.0124)

Constraints
-----------
- Normal approximation: needs roughly n*p >= 10 and n*(1-p) >= 10 in each arm.

Approach ladder
---------------
1. Brute force — permutation test: O(n_perm * n) time, exact up to Monte Carlo error,
   no normal approximation.
2. Optimal    — z-test: O(1) from four counts. Matches the permutation p-value for large n.
3. Planning   — sample size from the formula: O(1); verified by simulating power,
   O(sims) with ``rng.binomial``.

Follow-ups
----------
- One- vs two-sided: decide before looking; one-sided halves p when z > 0.
- Multiple metrics/variants: Bonferroni alpha / m, or control the FDR.
- Peeking: use a fixed horizon or a sequential method (alpha spending).
- Unit of randomisation vs unit of analysis (users vs sessions): SE too small otherwise.
- Edge cases: SE == 0, n_a != n_b, alternative="larger" with z < 0 (p > 0.5).
"""
from __future__ import annotations

from math import erfc, sqrt
from statistics import NormalDist

import numpy as np

_N = NormalDist()


def two_proportion_ztest(x_a: int, n_a: int, x_b: int, n_b: int, alternative: str = "two-sided"):
    p_a, p_b = x_a / n_a, x_b / n_b
    pooled = (x_a + x_b) / (n_a + n_b)
    se = sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    if se == 0:
        raise ValueError("zero standard error: both arms all 0 or all 1")
    z = (p_b - p_a) / se
    if alternative == "two-sided":
        p = erfc(abs(z) / sqrt(2))          # = 2 * (1 - Phi(|z|)) without cancellation
    elif alternative == "larger":
        p = 0.5 * erfc(z / sqrt(2))         # = 1 - Phi(z)
    else:
        raise ValueError("alternative must be 'two-sided' or 'larger'")
    return z, p


def diff_ci(x_a: int, n_a: int, x_b: int, n_b: int, alpha: float = 0.05):
    p_a, p_b = x_a / n_a, x_b / n_b
    se = sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    z = _N.inv_cdf(1 - alpha / 2)
    d = p_b - p_a
    return d - z * se, d + z * se


def permutation_pvalue(x_a: int, n_a: int, x_b: int, n_b: int, n_perm: int = 10_000, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    outcomes = np.zeros(n_a + n_b)
    outcomes[: x_a + x_b] = 1.0
    observed = abs(x_b / n_b - x_a / n_a)
    hits = 0
    for _ in range(n_perm):
        perm = rng.permutation(outcomes)    # relabel users at random: H0 says labels don't matter
        d = perm[n_a:].mean() - perm[:n_a].mean()
        hits += abs(d) >= observed - 1e-12
    return (hits + 1) / (n_perm + 1)


def sample_size_per_arm(p1: float, p2: float, alpha: float = 0.05, power: float = 0.8) -> int:
    za, zb = _N.inv_cdf(1 - alpha / 2), _N.inv_cdf(power)
    pbar = (p1 + p2) / 2
    num = za * sqrt(2 * pbar * (1 - pbar)) + zb * sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    return int(np.ceil(num ** 2 / (p2 - p1) ** 2))


def simulated_power(p1: float, p2: float, n: int, alpha: float = 0.05, sims: int = 20_000, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    xa, xb = rng.binomial(n, p1, sims), rng.binomial(n, p2, sims)
    pooled = (xa + xb) / (2 * n)
    z = (xb - xa) / n / np.sqrt(pooled * (1 - pooled) * 2 / n)
    return float(np.mean(np.abs(z) >= _N.inv_cdf(1 - alpha / 2)))


def peeking_false_positive_rate(p: float = 0.1, n_per_look: int = 500, looks: int = 20,
                                alpha: float = 0.05, sims: int = 4000, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    xa = rng.binomial(n_per_look, p, (sims, looks)).cumsum(axis=1)   # A/A: no true effect
    xb = rng.binomial(n_per_look, p, (sims, looks)).cumsum(axis=1)
    n = n_per_look * np.arange(1, looks + 1)
    pooled = (xa + xb) / (2 * n)
    z = (xb - xa) / n / np.sqrt(pooled * (1 - pooled) * 2 / n)
    significant = np.abs(z) >= _N.inv_cdf(1 - alpha / 2)
    return float(significant.any(axis=1).mean())      # stopped at ANY look


def main() -> None:
    z, p = two_proportion_ztest(200, 2000, 250, 2000)
    print(f"A 200/2000 vs B 250/2000: z={z:.3f}  two-sided p={p:.4f}")
    print(f"one-sided (B > A) p={two_proportion_ztest(200, 2000, 250, 2000, 'larger')[1]:.4f}")
    lo, hi = diff_ci(200, 2000, 250, 2000)
    print(f"95% CI for p_b - p_a: ({lo:.4f}, {hi:.4f})")
    print(f"permutation p (10,000 shuffles): {permutation_pvalue(200, 2000, 250, 2000, seed=35):.4f}")
    n = sample_size_per_arm(0.10, 0.12)
    print("n per arm to detect 10% -> 12% (alpha .05, power .8):", n)
    print(f"simulated power at that n: {simulated_power(0.10, 0.12, n, seed=35):.3f}")
    print(f"A/A, test once at the end : {peeking_false_positive_rate(looks=1, n_per_look=10_000, seed=35):.3f}")
    print(f"A/A, peek 20 times, stop early: {peeking_false_positive_rate(seed=35):.3f}")
    try:
        two_proportion_ztest(0, 100, 0, 100)
    except ValueError as e:
        print("all-zero arms -> ValueError:", e)


if __name__ == "__main__":
    main()
