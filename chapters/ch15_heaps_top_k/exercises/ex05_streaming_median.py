"""
Exercise 05 — Streaming Median With Two Heaps                      [Tier: ★ Core]
Chapter 15 · Pattern: two heaps (max-heap low half, min-heap high half) · Target time: 25 min

Problem
-------
Design `MedianFinder` with `add(x)` and `median()`. After any number of adds (at least
one), `median()` returns the middle value, or the mean of the two middle values when the
count is even. `median()` before any add raises `ValueError`.
`solve(stream)` returns the median after each add.

Examples
--------
>>> solve([5, 15, 1, 3])
[5, 10.0, 5, 4.0]
>>> solve([2, 2])
[2, 2.0]

Constraints
-----------
- Up to 10^5 adds; values are ints. Results match `statistics.median` exactly
  (int for an odd count, float for an even count).

Hints
-----
- Push `-x` into the max-heap and negate on the way out.
- Always route a new value through `low` then `high`; this keeps every value in low <=
  every value in high without comparing anything yourself.
- Median: low's top when the count is odd, else the mean of the two tops.

Follow-ups
----------
- Sliding-window median: two heaps + lazy deletion (a dict of values to discard), or a
  sorted list with bisect (O(k) per step, simpler and often fast enough).
- Values in a small range (0..100): a counting array gives O(100) median.
- Percentile p instead of 50 %: size the halves as p : (1 - p).

Wrong-but-tempting
------------------
- Pushing x into whichever heap is smaller without the low->high hop: breaks the
  "every low <= every high" invariant (e.g. add 10 then 1).
- Forgetting to negate when READING low's top: median of [1, 3] comes out as 1.0.
"""
from __future__ import annotations

import bisect
import heapq
import random
import statistics


class MedianSort:
    """Rung 1."""

    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def add(self, x: int) -> None:
        raise NotImplementedError("TODO")

    def median(self) -> float:
        raise NotImplementedError("TODO")


class MedianInsort(MedianSort):
    """Rung 2: the list is always sorted."""

    def add(self, x: int) -> None:
        raise NotImplementedError("TODO")

    def median(self) -> float:
        raise NotImplementedError("TODO")


class MedianFinder:
    """Rung 3: two heaps."""

    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def add(self, x: int) -> None:
        raise NotImplementedError("TODO")

    def median(self) -> float:
        raise NotImplementedError("TODO")


def solve(stream: list[int], cls: type = MedianFinder) -> list[float]:
    raise NotImplementedError("TODO")


def main() -> None:
    for stream in ([5, 15, 1, 3], [2, 2], [10, 1], [-1, -2, -3, -4, -5], [7]):
        ans = solve(stream)
        agree = ans == solve(stream, MedianSort) == solve(stream, MedianInsort)
        print(f"{stream} -> {ans}  agree={agree}")
    mf = MedianFinder()
    for x in [5, 15, 1, 3, 8]:
        mf.add(x)
    print("after 5,15,1,3,8: low (max-heap) =", sorted(-v for v in mf.low),
          "high =", sorted(mf.high), "median =", mf.median())
    try:
        MedianFinder().median()
    except ValueError as e:
        print("empty -> ValueError:", e)
    rng = random.Random(15)
    data = [rng.randint(-50, 50) for _ in range(2000)]
    meds = solve(data)
    checks = range(0, len(data), 97)                 # spot-check every 97th prefix
    print("2000 random adds match statistics.median:",
          all(meds[i] == statistics.median(data[: i + 1]) for i in checks))


if __name__ == "__main__":
    main()
