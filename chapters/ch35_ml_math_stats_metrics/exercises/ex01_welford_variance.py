"""
Exercise 01 — Streaming Mean and Variance (Welford)              [Tier: ★ Core]
Chapter 35 · Pattern: one-pass statistics, numerical stability · Target time: 15 min

Problem
-------
A sensor sends floats one at a time; you may not store them. Keep a running mean and
variance, and let two workers that saw disjoint parts of the stream merge their summaries.

1. ``RunningStats``: ``push(x)``, ``mean``, ``variance(ddof=1)``, ``merge(other)``.
   ``ddof=1`` is the sample (unbiased) variance, divisor n - 1; ``ddof=0`` the population
   variance, divisor n. Raise ``ValueError`` when n <= ddof.
2. ``solve(xs, ddof=1)`` returns ``(mean, variance)`` of a list using ``RunningStats``.

Examples
--------
>>> solve([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0], ddof=0)
(5.0, 4.0)
>>> solve([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0], ddof=1)[1] == 32 / 7
True

Constraints
-----------
- Values may share a huge offset (1e9 + small noise): the answer must stay accurate.

Hints
-----
- Keep only n, mean and m2 (the sum of squared deviations from the current mean).
- Update order matters: compute delta with the *old* mean, then update the mean, then
  multiply delta by the deviation from the *new* mean.
- Merge: the combined m2 needs a correction term for the gap between the two means.
- Rungs: naive_variance (sum of squares), two_pass_variance, then RunningStats.

Wrong-but-tempting
------------------
- (sum(x^2) - n*mean^2) / (n - 1): returns 0.0 (or a negative number) for data near 1e9.
- Dividing by n when the question asks for the sample variance (ddof=1), or vice versa.
- Merging by averaging the two variances: ignores the means' difference and the sizes.

Follow-ups
----------
- Exponentially weighted variance for drifting streams.
- Covariance: the same update with (x - mean_x) * (y - new mean_y).
- Why ddof=1? E[sum((x - xbar)^2)] = (n - 1) * sigma^2, because xbar is fitted to the data.
- Edge cases: n = 0, n = 1 with ddof=1, all-equal values, merge with an empty summary.
"""
from __future__ import annotations


def naive_variance(xs: list[float], ddof: int = 1) -> float:
    raise NotImplementedError("TODO")


def two_pass_variance(xs: list[float], ddof: int = 1) -> float:
    raise NotImplementedError("TODO")


class RunningStats:
    def __init__(self) -> None:
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0                      # sum of squared deviations from the current mean

    def push(self, x: float) -> None:
        raise NotImplementedError("TODO")

    def variance(self, ddof: int = 1) -> float:
        raise NotImplementedError("TODO")

    def merge(self, other: "RunningStats") -> "RunningStats":
        raise NotImplementedError("TODO")


def solve(xs: list[float], ddof: int = 1) -> tuple[float, float]:
    raise NotImplementedError("TODO")


def main() -> None:
    data = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    print("population (ddof=0):", solve(data, ddof=0))
    print("sample     (ddof=1):", tuple(round(v, 6) for v in solve(data, ddof=1)), "  32/7 =", round(32 / 7, 6))

    shifted = [1e9 + v for v in (4.0, 7.0, 13.0, 16.0)]   # true sample variance is 30
    print("offset 1e9, true sample variance 30:")
    print("  naive    :", naive_variance(shifted))
    print("  two-pass :", two_pass_variance(shifted))
    print("  welford  :", solve(shifted)[1])

    a, b = RunningStats(), RunningStats()
    for x in data[:3]:
        a.push(x)
    for x in data[3:]:
        b.push(x)
    m = a.merge(b)
    print("merged halves: n =", m.n, " mean =", m.mean, " var(ddof=0) =", m.variance(0))
    print("merge with empty keeps stats:", a.merge(RunningStats()).variance(0) == a.variance(0))
    try:
        solve([3.0], ddof=1)
    except ValueError as e:
        print("one value, ddof=1 -> ValueError:", e)


if __name__ == "__main__":
    main()
