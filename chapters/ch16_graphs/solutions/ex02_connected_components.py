"""
Exercise 02 — Connected Components (DFS)                [Tier: ★ Core]
Chapter 16 · Pattern: DFS recursive + iterative · Target time: 15 min

Problem
-------
An undirected graph has ``n`` nodes labelled 0..n-1 and a list of edges. Return its
connected components as a list of sorted node lists, the list itself sorted by
smallest member. Also provide ``count_components(n, edges)``.

Examples
--------
>>> solve(5, [(0, 1), (1, 2), (3, 4)])
[[0, 1, 2], [3, 4]]
>>> count_components(3, [])
3

Constraints
-----------
- 0 <= n <= 10**5, 0 <= len(edges) <= 2 * 10**5. Self-loops and duplicate edges allowed.

Approach ladder
---------------
1. Brute force — for each node, BFS to find everything it reaches, then dedupe the
   reachable sets: O(V * (V + E)). Repeats work for every member of a component.
2. Improved   — recursive DFS with a shared ``seen`` set: each node and edge touched
   once, O(V + E). But Python's default recursion limit (~1000) crashes on a long path.
3. Optimal    — iterative DFS with an explicit stack: same O(V + E), no recursion
   limit. (Union-Find, Ex 09, also solves it in ~O(E α(V)) and works with streaming edges.)

Hints
-----
- Build an adjacency list first.
- Mark a node seen when you PUSH it (or when you pop it and skip if seen) — be consistent.
- Outer loop over all nodes so isolated nodes become their own component.

Follow-ups
----------
- Number of provinces given an adjacency matrix.
- Edges arrive one at a time and you must report the count after each: Union-Find.
- Largest component size; component of a given node only.
"""
from __future__ import annotations

import sys
from collections import deque


def _adj(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:  # keep
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def brute_force(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    """Reachable set from every node, then dedupe. O(V * (V + E))."""
    adj = _adj(n, edges)
    groups = set()
    for start in range(n):
        seen = {start}
        q = deque([start])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        groups.add(tuple(sorted(seen)))
    return sorted(list(g) for g in groups)


def dfs_recursive(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    """O(V + E) but limited by the recursion depth."""
    adj = _adj(n, edges)
    seen = [False] * n
    comps = []

    def dfs(u: int, comp: list[int]) -> None:
        seen[u] = True
        comp.append(u)
        for v in adj[u]:
            if not seen[v]:
                dfs(v, comp)

    for s in range(n):
        if not seen[s]:
            comp: list[int] = []
            dfs(s, comp)
            comps.append(sorted(comp))
    return comps


def solve(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    """Iterative DFS with an explicit stack. O(V + E) time and space."""
    adj = _adj(n, edges)
    seen = [False] * n
    comps = []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True              # mark on push: each node enters the stack once
        stack, comp = [s], []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        comps.append(sorted(comp))
    return comps


def count_components(n: int, edges: list[tuple[int, int]]) -> int:
    return len(solve(n, edges))


def main() -> None:
    cases = [
        (5, [(0, 1), (1, 2), (3, 4)]),
        (6, [(0, 1), (2, 3), (3, 4), (4, 2)]),
        (3, []),
        (1, [(0, 0)]),
        (0, []),
    ]
    for n, edges in cases:
        comps = solve(n, edges)
        same = comps == brute_force(n, edges) == dfs_recursive(n, edges)
        print(f"n={n} edges={edges}\n   components={comps} count={len(comps)} all_rungs_agree={same}")

    # A path of 5000 nodes: recursive DFS exceeds the default recursion limit.
    n = 5000
    path = [(i, i + 1) for i in range(n - 1)]
    print("recursion limit:", sys.getrecursionlimit())
    try:
        dfs_recursive(n, path)
        print("recursive DFS on 5000-node path: ok")
    except RecursionError:
        print("recursive DFS on 5000-node path: RecursionError")
    print("iterative DFS on 5000-node path: count =", count_components(n, path))


if __name__ == "__main__":
    main()
