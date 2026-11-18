"""
Exercise 09 — Union-Find (Disjoint Set Union)           [Tier: ★ Core]
Chapter 16 · Pattern: DSU with path compression + union by rank · Target time: 20 min

Problem
-------
Implement ``DSU(n)`` with ``find(x)``, ``union(a, b) -> bool`` (False if already joined),
``connected(a, b)``, and attribute ``count`` (number of disjoint sets). Use it for:

- ``solve(edges)`` — Redundant Connection: a tree on nodes 1..n had ONE extra edge added;
  return the last edge in input order whose removal leaves a tree.
- ``count_provinces(matrix)`` — number of connected groups in an adjacency matrix.
- ``accounts_merge(accounts)`` — each account is [name, email, ...]; accounts sharing any
  email belong to the same person. Return [name, *sorted emails] per person, sorted.

Examples
--------
>>> solve([(1, 2), (1, 3), (2, 3)])
(2, 3)
>>> count_provinces([[1, 1, 0], [1, 1, 0], [0, 0, 1]])
2

Constraints
-----------
- n up to 10**5; any sequence of unions and finds.

Approach ladder
---------------
1. Brute force — "quick-find": store a label per node; union relabels every node of one
   set: find O(1), union O(n) -> O(n * m) for m unions.
2. Improved   — "quick-union": parent pointers, union links roots. Finds walk to the
   root; without balancing, trees degenerate into chains -> O(n) per find.
3. Optimal    — union by rank (attach the shorter tree under the taller) + path
   compression (point visited nodes straight at the root): amortised O(α(n)) per
   operation, where α is the inverse Ackermann function (<= 4 for any practical n).

Hints
-----
- ``parent[i] = i`` initially; a root is its own parent.
- Path halving in a loop avoids recursion: ``parent[x] = parent[parent[x]]``.
- ``union`` returns False when roots are equal — that is the cycle signal.
- Accounts merge: union emails (not accounts); map each email to its first account's name.

Follow-ups
----------
- Number of Islands II (cells added online), Kruskal's MST (Ex 17).
- Weighted DSU (evaluate division), DSU with parity (online bipartiteness).
- Deletions are NOT supported — mention offline reverse processing.
"""
from __future__ import annotations

from collections import defaultdict


class QuickFind:
    """Brute force: label array; union is O(n)."""

    def __init__(self, n: int) -> None:
        self.label = list(range(n))
        self.count = n

    def find(self, x: int) -> int:
        return self.label[x]

    def union(self, a: int, b: int) -> bool:
        la, lb = self.label[a], self.label[b]
        if la == lb:
            return False
        for i, lab in enumerate(self.label):
            if lab == la:
                self.label[i] = lb
        self.count -= 1
        return True


class DSU:
    """Union by rank + path compression (path halving). ~O(α(n)) amortised per op."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path halving
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra                 # attach shorter tree under taller
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.count -= 1
        return True

    def connected(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)


def brute_force(edges: list[tuple[int, int]]) -> tuple[int, int]:
    """Redundant connection by trying to delete each edge (last first) and checking it's a tree."""
    n = len(edges)
    for skip in range(n - 1, -1, -1):
        qf = QuickFind(n + 1)
        ok = True
        for i, (u, v) in enumerate(edges):
            if i != skip and not qf.union(u, v):
                ok = False
                break
        if ok:
            return edges[skip]
    return ()


def solve(edges: list[tuple[int, int]]) -> tuple[int, int]:
    """First edge whose endpoints are already connected. O(n α(n))."""
    dsu = DSU(len(edges) + 1)
    for u, v in edges:
        if not dsu.union(u, v):
            return (u, v)
    return ()


def count_provinces(matrix: list[list[int]]) -> int:
    n = len(matrix)
    dsu = DSU(n)
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j]:
                dsu.union(i, j)
    return dsu.count


def accounts_merge(accounts: list[list[str]]) -> list[list[str]]:
    email_id: dict[str, int] = {}
    owner: dict[str, str] = {}
    for acc in accounts:
        for email in acc[1:]:
            if email not in email_id:
                email_id[email] = len(email_id)
                owner[email] = acc[0]
    dsu = DSU(len(email_id))
    for acc in accounts:
        first = email_id[acc[1]] if len(acc) > 1 else None
        for email in acc[2:]:
            dsu.union(first, email_id[email])
    groups: dict[int, list[str]] = defaultdict(list)
    for email, i in email_id.items():
        groups[dsu.find(i)].append(email)
    return sorted([owner[es[0]]] + sorted(es) for es in groups.values())


def main() -> None:
    dsu = DSU(6)
    print("start      parent=", dsu.parent, "rank=", dsu.rank, "count=", dsu.count)
    for a, b in [(0, 1), (2, 3), (1, 3), (4, 5), (0, 2)]:
        joined = dsu.union(a, b)
        print(f"union({a},{b}) {'joined ' if joined else 'already'} parent={dsu.parent} rank={dsu.rank} count={dsu.count}")
    print("connected(0,3):", dsu.connected(0, 3), "| connected(0,4):", dsu.connected(0, 4))

    # Without union by rank, a chain forms; path compression flattens it on the first find.
    chain = DSU(5)
    chain.parent = [0, 0, 1, 2, 3]          # hand-built chain 4 -> 3 -> 2 -> 1 -> 0
    print("chain before find(4):", chain.parent)
    chain.find(4)
    print("chain after  find(4):", chain.parent, "(path halving)")

    for edges in [[(1, 2), (1, 3), (2, 3)], [(1, 2), (2, 3), (3, 4), (1, 4), (1, 5)]]:
        print(f"redundant {edges}: {solve(edges)} (brute {brute_force(edges)})")
    print("provinces:", count_provinces([[1, 1, 0], [1, 1, 0], [0, 0, 1]]))
    accounts = [
        ["Ann", "a@x", "a2@x"], ["Bob", "b@x"], ["Ann", "a3@x", "a@x"], ["Ann", "solo@x"],
    ]
    for row in accounts_merge(accounts):
        print("merged:", row)


if __name__ == "__main__":
    main()
