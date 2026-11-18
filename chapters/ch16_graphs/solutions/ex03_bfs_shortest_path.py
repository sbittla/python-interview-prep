"""
Exercise 03 — BFS Shortest Path (unweighted)            [Tier: ★ Core]
Chapter 16 · Pattern: BFS with parent pointers · Target time: 15 min

Problem
-------
Given an undirected, unweighted graph as an adjacency dict and two nodes ``src`` and
``dst``, return one shortest path from ``src`` to ``dst`` as a list of nodes, or ``[]``
if ``dst`` is unreachable. Neighbours are explored in the order stored in the dict,
so the returned path is deterministic. Also write ``bfs_layers(adj, src)`` that returns
the nodes grouped by distance from ``src``.

Examples
--------
>>> adj = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"], "D": ["B", "C"]}
>>> solve(adj, "A", "D")
['A', 'B', 'D']
>>> bfs_layers(adj, "A")
[['A'], ['B', 'C'], ['D']]

Constraints
-----------
- Up to 10**5 nodes and edges. ``src == dst`` returns ``[src]``.

Approach ladder
---------------
1. Brute force — DFS enumerating every simple path, keep the shortest. Exponential
   (a grid has astronomically many simple paths).
2. Improved   — BFS that stores the whole path in the queue: correct and O(V + E)
   visits, but copying paths costs O(V) per enqueue -> O(V^2) memory in the worst case.
3. Optimal    — BFS that stores only a ``parent`` dict, then walks parents back from
   ``dst``: O(V + E) time, O(V) space. BFS is correct because it settles nodes in
   non-decreasing distance order: the first time a node is seen is via a shortest path.

Hints
-----
- Mark visited when ENQUEUING, not when dequeuing, or nodes enter the queue many times.
- To reconstruct: follow parent[] from dst to src, then reverse.
- Process the queue level by level (``for _ in range(len(q))``) to get layers.

Follow-ups
----------
- All shortest paths (store a list of parents per node).
- Weighted edges -> Dijkstra (Ex 10); weights 0/1 -> 0-1 BFS (Ex 11).
- Huge graph with known target -> bidirectional BFS (Ex 12).
"""
from __future__ import annotations

from collections import deque


def brute_force(adj: dict, src, dst) -> list:
    """Enumerate all simple paths with DFS; keep the shortest. Exponential."""
    best: list = []

    def dfs(u, path: list, on_path: set) -> None:
        nonlocal best
        if best and len(path) >= len(best):
            return                      # cannot improve
        if u == dst:
            best = list(path)
            return
        for v in adj.get(u, []):
            if v not in on_path:
                on_path.add(v)
                path.append(v)
                dfs(v, path, on_path)
                path.pop()
                on_path.remove(v)

    dfs(src, [src], {src})
    return best


def bfs_with_paths(adj: dict, src, dst) -> list:
    """BFS that carries whole paths in the queue: simple, but O(V) copy per push."""
    q = deque([[src]])
    seen = {src}
    while q:
        path = q.popleft()
        if path[-1] == dst:
            return path
        for v in adj.get(path[-1], []):
            if v not in seen:
                seen.add(v)
                q.append(path + [v])
    return []


def solve(adj: dict, src, dst) -> list:
    """BFS with parent pointers. O(V + E) time, O(V) space."""
    parent = {src: None}
    q = deque([src])
    while q:
        u = q.popleft()
        if u == dst:
            break
        for v in adj.get(u, []):
            if v not in parent:         # parent doubles as the visited set
                parent[v] = u
                q.append(v)
    if dst not in parent:
        return []
    path = []
    node = dst
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]


def bfs_layers(adj: dict, src) -> list[list]:
    """Nodes grouped by BFS distance (level-order processing)."""
    seen = {src}
    layer = [src]
    layers = []
    while layer:
        layers.append(layer)
        nxt = []
        for u in layer:
            for v in adj.get(u, []):
                if v not in seen:
                    seen.add(v)
                    nxt.append(v)
        layer = nxt
    return layers


def main() -> None:
    #   A --- B --- E --- G
    #   |     |     |
    #   C --- D --- F
    adj = {
        "A": ["B", "C"], "B": ["A", "D", "E"], "C": ["A", "D"], "D": ["B", "C", "F"],
        "E": ["B", "F", "G"], "F": ["D", "E"], "G": ["E"], "Z": [],
    }
    print("BFS layer trace from A:")
    for d, layer in enumerate(bfs_layers(adj, "A")):
        print(f"  distance {d}: {layer}")
    for src, dst in [("A", "G"), ("C", "G"), ("A", "A"), ("A", "Z")]:
        p = solve(adj, src, dst)
        agree = p == bfs_with_paths(adj, src, dst) and len(p) == len(brute_force(adj, src, dst))
        print(f"shortest {src}->{dst}: {p}  edges={max(len(p) - 1, -1)}  rungs_agree={agree}")


if __name__ == "__main__":
    main()
