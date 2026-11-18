"""
Exercise 06 — Bipartite Check / Two-Colouring           [Tier: ★ Core]
Chapter 16 · Pattern: BFS colouring · Target time: 15 min

Problem
-------
``adj`` is an undirected graph given as a list where ``adj[u]`` lists the neighbours of
node u (the graph may be disconnected). Return a colouring ``list[int]`` of 0/1 such that
every edge joins different colours, or ``None`` if impossible (the graph is not
bipartite). Colour the smallest node of each component 0, then BFS.
``is_bipartite(adj)`` returns a bool. ``possible_bipartition(n, dislikes)`` answers:
can people 1..n be split into two groups so no pair in ``dislikes`` shares a group?

Examples
--------
>>> solve([[1, 3], [0, 2], [1, 3], [0, 2]])
[0, 1, 0, 1]
>>> solve([[1, 2], [0, 2], [0, 1]]) is None
True

Constraints
-----------
- 1 <= n <= 10**4. No self-loops (a self-loop would make the graph non-bipartite).

Approach ladder
---------------
1. Brute force — try all 2^n colourings and check every edge: O(2^n * E).
2. Improved   — backtracking colouring with early rejection: still exponential in
   the worst case for general k-colouring, but for k = 2 the first colour forces all
   others, which leads to...
3. Optimal    — BFS (or DFS) propagation: colour a start node 0, every neighbour gets
   the opposite colour; a conflict means an odd cycle. O(V + E). Equivalent theorem:
   a graph is bipartite iff it has no odd-length cycle.

Hints
-----
- Loop over every node as a potential start: components are independent.
- Use colour array initialised to -1 (= unvisited); ``1 - colour[u]`` flips.
- Union-Find alternative: union all neighbours of u together; u must never be in
  the same set as any neighbour.

Follow-ups
----------
- Return the odd cycle as a certificate.
- k-colouring for k >= 3 is NP-complete — say so, and offer backtracking.
- Is graph bipartite when edges arrive online -> DSU with parity.
"""
from __future__ import annotations

from collections import deque
from itertools import product


def brute_force(adj: list[list[int]]) -> list[int] | None:
    """Try every 0/1 assignment (n <= ~16). Returns the lexicographically smallest valid one."""
    n = len(adj)
    for colours in product((0, 1), repeat=n):
        if all(colours[u] != colours[v] for u in range(n) for v in adj[u]):
            return list(colours)
    return None


def solve(adj: list[list[int]]) -> list[int] | None:
    """BFS two-colouring. O(V + E)."""
    n = len(adj)
    colour = [-1] * n
    for start in range(n):
        if colour[start] != -1:
            continue
        colour[start] = 0
        q = deque([start])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if colour[v] == -1:
                    colour[v] = 1 - colour[u]
                    q.append(v)
                elif colour[v] == colour[u]:
                    return None          # edge inside one colour => odd cycle
    return colour


def is_bipartite(adj: list[list[int]]) -> bool:
    return solve(adj) is not None


def possible_bipartition(n: int, dislikes: list[tuple[int, int]]) -> bool:
    adj: list[list[int]] = [[] for _ in range(n)]
    for a, b in dislikes:                 # people are 1-indexed
        adj[a - 1].append(b - 1)
        adj[b - 1].append(a - 1)
    return is_bipartite(adj)


def main() -> None:
    square = [[1, 3], [0, 2], [1, 3], [0, 2]]       # even cycle 0-1-2-3-0
    triangle = [[1, 2], [0, 2], [0, 1]]             # odd cycle
    two_parts = [[1], [0], [3, 4], [2, 4], [2, 3]]   # edge + triangle
    isolated = [[], [], []]
    for name, g in [("square", square), ("triangle", triangle), ("edge+triangle", two_parts), ("isolated", isolated)]:
        print(f"{name:<14} colouring={solve(g)}  brute={brute_force(g)}")
    print("""
square as layers (BFS from 0):
   colour 0: 0   2
   colour 1: 1   3""")
    print("possible_bipartition(4, [(1,2),(1,3),(2,4)]) =", possible_bipartition(4, [(1, 2), (1, 3), (2, 4)]))
    print("possible_bipartition(3, [(1,2),(1,3),(2,3)]) =", possible_bipartition(3, [(1, 2), (1, 3), (2, 3)]))


if __name__ == "__main__":
    main()
