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

Approach ladder
---------------
1. Plain list — update O(1), range query O(n). Fine for few queries.
2. Prefix-sum array — query O(1), but every update rebuilds: O(n).
3. Fenwick tree — both O(log n), n + 1 cells, ~15 lines; needs an
   invertible operation (sum, xor). Segment tree — both O(log n), 2n cells
   (iterative version), works for any associative operation (min, max, gcd;
   this bottom-up query loop also assumes the operation is commutative).

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
        i += 1
        while i <= self.n:
            self.tree[i] += delta
            self.touched += 1
            i += i & -i                          # jump to the next covering cell

    def prefix_sum(self, i: int) -> int:
        total = 0
        while i > 0:
            total += self.tree[i]
            self.touched += 1
            i -= i & -i                          # drop the lowest set bit
        return total

    def range_sum(self, lo: int, hi: int) -> int:
        return self.prefix_sum(hi) - self.prefix_sum(lo)


class SegmentTreeMin:
    def __init__(self, values: list[int]) -> None:
        self.n = len(values)
        self.tree = [math.inf] * self.n + list(values)   # leaves at n..2n-1
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = min(self.tree[2 * i], self.tree[2 * i + 1])
        self.touched = 0

    def set(self, i: int, value: int) -> None:
        i += self.n
        self.tree[i] = value
        self.touched += 1
        while i > 1:
            i //= 2
            self.tree[i] = min(self.tree[2 * i], self.tree[2 * i + 1])
            self.touched += 1

    def range_min(self, lo: int, hi: int):
        if not 0 <= lo < hi <= self.n:
            raise ValueError("need 0 <= lo < hi <= n")
        best, lo, hi = math.inf, lo + self.n, hi + self.n
        while lo < hi:
            if lo & 1:
                best = min(best, self.tree[lo]); lo += 1; self.touched += 1
            if hi & 1:
                hi -= 1; best = min(best, self.tree[hi]); self.touched += 1
            lo //= 2; hi //= 2
        return best


def cross_check(n: int, ops: int, seed: int = 0) -> bool:
    rng = random.Random(seed)
    values = [rng.randint(-50, 50) for _ in range(n)]
    fen, seg, plain = Fenwick(values), SegmentTreeMin(values), list(values)
    for _ in range(ops):
        i = rng.randrange(n)
        if rng.random() < 0.5:
            v = rng.randint(-50, 50)
            fen.add(i, v - plain[i]); seg.set(i, v); plain[i] = v
        else:
            lo = rng.randrange(n); hi = rng.randint(lo + 1, n)
            if fen.range_sum(lo, hi) != sum(plain[lo:hi]):
                return False
            if seg.range_min(lo, hi) != min(plain[lo:hi]):
                return False
    return True


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
