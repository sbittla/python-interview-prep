"""
Exercise 03 — Union-Find Cost Counter                   [Tier: ◆ Extended]
Chapter 22 · Pattern: amortised analysis of union-find · Target time: 25 min

Problem
-------
Implement ``UnionFind(n, compress, by_rank)`` with ``find`` and ``union``
(union links the root of the first argument's set under the root of the
second unless rank decides otherwise). Count ``hops``: the number of
parent-pointer links followed while searching for a root (path-compression
rewrites do not count as hops).

``adversarial_hops(n, compress, by_rank)`` runs this fixed sequence and returns
the total hops:

    union(0, 1), union(1, 2), ..., union(n-2, n-1)    # builds a chain
    find(0), find(1), ..., find(n-1)                  # deepest node first

The chain is easy for rank, so add a second sequence that is hard for it:
``binomial_find_hops(n, compress, by_rank, rounds)`` (n a power of two) merges
blocks of size 1, 2, 4, ... pairwise with union(i, i + s), which builds a tree
of height log2 n even with union by rank, then calls find on every node
``rounds`` times and returns only the hops spent in those finds.

Compare the four combinations of the two optimisations. Union-find itself is
taught in §16.9; this exercise measures *why* both optimisations matter.

Examples
--------
>>> adversarial_hops(5, compress=False, by_rank=False)
10
>>> adversarial_hops(5, compress=True, by_rank=True)
6
>>> binomial_find_hops(8, compress=False, by_rank=True, rounds=1)
12

Constraints
-----------
- 1 <= n <= 10**5. ``find`` must be iterative (a chain of 10**5 would overflow
  the recursion limit).

Hints
-----
- find: first loop walks to the root counting hops; if compress, a second
  loop repoints every node on the path at the root (no hops counted).
- union by rank: the root with the smaller rank goes under the other; ranks
  grow only when they were equal.
- Keep find iterative: a 10**5 chain would exceed the recursion limit.
- binomial_find_hops: record uf.hops before the find rounds and subtract.

Follow-ups
----------
- Why can a single find still cost O(log n) with both optimisations? Amortised
  bounds limit the total, not each call.
- Union by size gives the same bounds as union by rank.
"""
from __future__ import annotations


class UnionFind:
    def __init__(self, n: int, compress: bool = True, by_rank: bool = True) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n
        self.compress, self.by_rank = compress, by_rank
        self.hops = 0

    def find(self, x: int) -> int:
        raise NotImplementedError("TODO")

    def union(self, a: int, b: int) -> bool:
        raise NotImplementedError("TODO")

    def height(self) -> int:
        """Longest node-to-root path (diagnostic; does not count hops)."""
        best = 0
        for x in range(len(self.parent)):
            d = 0
            while self.parent[x] != x:
                x, d = self.parent[x], d + 1
            best = max(best, d)
        return best


def adversarial_hops(n: int, compress: bool, by_rank: bool) -> int:
    raise NotImplementedError("TODO")


def chain_height(n: int, by_rank: bool) -> int:
    uf = UnionFind(n, compress=False, by_rank=by_rank)
    for i in range(n - 1):
        uf.union(i, i + 1)
    return uf.height()


def binomial_find_hops(n: int, compress: bool, by_rank: bool, rounds: int = 3) -> int:
    raise NotImplementedError("TODO")


CONFIGS = [("naive", False, False), ("compress only", True, False),
           ("rank only", False, True), ("compress + rank", True, True)]


def main() -> None:
    print(f"{'config':16} {'n=1000':>8} {'n=2000':>8} {'n=4000':>8}  growth x2")
    for name, compress, by_rank in CONFIGS:
        hops = [adversarial_hops(n, compress, by_rank) for n in (1000, 2000, 4000)]
        print(f"{name:16} {hops[0]:>8} {hops[1]:>8} {hops[2]:>8}  {hops[2] / hops[1]:.2f}")
    print(f"binomial merge, 3 rounds of finds, hops per find:")
    for name, compress, by_rank in CONFIGS:
        per = [binomial_find_hops(n, compress, by_rank) / (3 * n) for n in (1024, 4096)]
        print(f"  {name:16} n=1024: {per[0]:.2f}  n=4096: {per[1]:.2f}")
    print(f"naive hops == n(n-1)/2 at n=4000: {adversarial_hops(4000, False, False) == 4000 * 3999 // 2}")
    print(f"chain height n=4000: naive={chain_height(4000, False)} rank={chain_height(4000, True)}")
    uf = UnionFind(1)
    print(f"single element: find(0)={uf.find(0)} union(0,0)={uf.union(0, 0)} hops={uf.hops}")


if __name__ == "__main__":
    main()
