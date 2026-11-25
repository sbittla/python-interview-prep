"""
Exercise 05 — Fenwick Tree and Segment Tree, Cross-Checked   [Tier: ○ Reference]
Chapter 22 · Pattern: range queries with point updates · Target time: 30 min

Problem
-------
An array of n integers receives a mix of point updates and range queries.

- ``Fenwick(values)``: ``add(i, delta)``, ``prefix_sum(i)`` (sum of
  values[0..i-1]) and ``range_sum(lo, hi)`` (sum of values[lo..hi-1]).
- ``SegmentTreeMin(values)``: ``set(i, value)`` and ``range_min(lo, hi)`` over
  values[lo..hi-1] (lo < hi). Min has no inverse, so a Fenwick prefix trick
  cannot answer it; a segment tree can.

Both count ``touched``: tree cells read or written. ``cross_check(n, ops,
seed)`` runs random operations on both trees and on a plain list (brute force)
and returns True when every answer agrees.

Examples
--------
>>> f = Fenwick([5, 1, 4, 2]); f.range_sum(1, 3)
5
>>> f.add(2, 10); f.prefix_sum(4)
22
>>> SegmentTreeMin([5, 1, 4, 2]).range_min(2, 4)
2

Constraints
-----------
- 1 <= n <= 10**5; indices 0-based; half-open ranges [lo, hi).

Hints
-----
- Fenwick is 1-based inside: add walks i += i & -i, prefix walks
  i -= i & -i. Count one ``touched`` per cell visited.
- range_sum(lo, hi) = prefix_sum(hi) - prefix_sum(lo).
- Segment tree (iterative, leaves at n..2n-1): after setting a leaf, recompute
  parents i //= 2 up to the root. For a query, move lo and hi inward: take
  tree[lo] when lo is odd, tree[hi - 1] when hi is odd, then halve both.
- cross_check: compare both trees with sum/min over the plain list slice.

Follow-ups
----------
- Range update + point query: Fenwick over the difference array.
- Range update + range query: segment tree with lazy propagation.
"""
from __future__ import annotations

import math
import random


class Fenwick:
    def __init__(self, values: list[int]) -> None:
        self.n = len(values)
        self.tree = [0] * (self.n + 1)          # 1-based internally
        self.touched = 0
        for i, v in enumerate(values):
            self.add(i, v)
        self.touched = 0

    def add(self, i: int, delta: int) -> None:
        raise NotImplementedError("TODO")

    def prefix_sum(self, i: int) -> int:
        raise NotImplementedError("TODO")

    def range_sum(self, lo: int, hi: int) -> int:
        raise NotImplementedError("TODO")


class SegmentTreeMin:
    def __init__(self, values: list[int]) -> None:
        self.n = len(values)
        self.tree = [math.inf] * self.n + list(values)   # leaves at n..2n-1
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = min(self.tree[2 * i], self.tree[2 * i + 1])
        self.touched = 0

    def set(self, i: int, value: int) -> None:
        raise NotImplementedError("TODO")

    def range_min(self, lo: int, hi: int):
        raise NotImplementedError("TODO")


def cross_check(n: int, ops: int, seed: int = 0) -> bool:
    raise NotImplementedError("TODO")


def max_touched_per_query(n: int) -> tuple[int, int]:
    """Worst cells touched by one range query over every [lo, hi) for small n."""
    fen, seg = Fenwick(list(range(n))), SegmentTreeMin(list(range(n)))
    worst_f = worst_s = 0
    for lo in range(n):
        for hi in range(lo + 1, n + 1):
            fen.touched = seg.touched = 0
            fen.range_sum(lo, hi); seg.range_min(lo, hi)
            worst_f, worst_s = max(worst_f, fen.touched), max(worst_s, seg.touched)
    return worst_f, worst_s


def main() -> None:
    f = Fenwick([5, 1, 4, 2])
    print(f"range_sum(1, 3) = {f.range_sum(1, 3)}")
    f.add(2, 10)
    print(f"after add(2, 10): prefix_sum(4) = {f.prefix_sum(4)}")
    print(f"range_min(2, 4) = {SegmentTreeMin([5, 1, 4, 2]).range_min(2, 4)}")
    for n, ops, seed in [(1, 50, 1), (7, 500, 2), (100, 2000, 3), (1000, 2000, 4)]:
        print(f"cross_check n={n:<5} ops={ops:<5}: {cross_check(n, ops, seed)}")
    print(" n    worst cells/query  Fenwick  segment   2*log2(n)")
    for n in (16, 64, 256):
        wf, ws = max_touched_per_query(n)
        print(f"{n:>4}                     {wf:>5}  {ws:>7}   {2 * math.log2(n):>9.0f}")


if __name__ == "__main__":
    main()
