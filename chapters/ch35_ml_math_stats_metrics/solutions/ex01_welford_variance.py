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

Approach ladder
---------------
1. Brute force — textbook one-pass formula (sum(x^2) - n*mean^2) / (n - ddof). O(n) time,
   O(1) space, but subtracts two nearly equal huge numbers: catastrophic cancellation.
2. Improved   — two passes: mean first, then sum((x - mean)^2). Accurate, O(n) time, but
   needs the data twice (O(n) storage for a stream).
3. Optimal    — Welford: delta = x - mean; mean += delta / n; m2 += delta * (x - mean).
   One pass, O(1) per update, O(1) space, accurate. Merging two summaries (Chan et al.):
   delta = mean_b - mean_a; m2 = m2_a + m2_b + delta^2 * n_a * n_b / n. O(1).

Follow-ups
----------
- Exponentially weighted variance for drifting streams.
- Covariance: the same update with (x - mean_x) * (y - new mean_y).
- Why ddof=1? E[sum((x - xbar)^2)] = (n - 1) * sigma^2, because xbar is fitted to the data.
- Edge cases: n = 0, n = 1 with ddof=1, all-equal values, merge with an empty summary.
"""
from __future__ import annotations


def naive_variance(xs: list[float], ddof: int = 1) -> float:
    n = len(xs)
    if n <= ddof:
        raise ValueError("need more than ddof values")
    s = sum(xs)
    sq = sum(x * x for x in xs)
    return (sq - s * s / n) / (n - ddof)


def two_pass_variance(xs: list[float], ddof: int = 1) -> float:
    n = len(xs)
    if n <= ddof:
        raise ValueError("need more than ddof values")
    mean = sum(xs) / n
    return sum((x - mean) ** 2 for x in xs) / (n - ddof)


class RunningStats:
    def __init__(self) -> None:
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0                      # sum of squared deviations from the current mean

    def push(self, x: float) -> None:
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (x - self.mean)  # old delta times new deviation

    def variance(self, ddof: int = 1) -> float:
        if self.n <= ddof:
            raise ValueError("need more than ddof values")
        return self.m2 / (self.n - ddof)

    def merge(self, other: "RunningStats") -> "RunningStats":
        out = RunningStats()
        out.n = self.n + other.n
        if out.n == 0:
            return out
        delta = other.mean - self.mean
        out.mean = self.mean + delta * other.n / out.n
        out.m2 = self.m2 + other.m2 + delta * delta * self.n * other.n / out.n
        return out


def solve(xs: list[float], ddof: int = 1) -> tuple[float, float]:
    rs = RunningStats()
    for x in xs:
        rs.push(x)
    return rs.mean, rs.variance(ddof)


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
