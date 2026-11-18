"""
Exercise 07 — Cycle Detection (undirected and directed)  [Tier: ★ Core]
Chapter 16 · Pattern: DFS parent tracking / three-colour DFS · Target time: 20 min

Problem
-------
(a) ``has_cycle_undirected(n, edges)``: does an undirected graph (no duplicate edges,
no self-loops) contain a cycle?
(b) ``solve(n, edges)``: does a DIRECTED graph contain a cycle?
(c) ``find_cycle(n, edges)``: return one directed cycle as a node list that starts and
ends at the same node (e.g. [1, 2, 3, 1]), or [] if acyclic. Search starts from nodes
in increasing order and follows edges in input order, so the answer is deterministic.

Examples
--------
>>> has_cycle_undirected(3, [(0, 1), (1, 2), (2, 0)])
True
>>> solve(3, [(0, 1), (1, 2), (0, 2)])
False
>>> find_cycle(4, [(0, 1), (1, 2), (2, 3), (3, 1)])
[1, 2, 3, 1]

Constraints
-----------
- 0 <= n <= 10**5.

Approach ladder
---------------
Directed:
1. Brute force — for every edge u->v, ask "can v reach u?" with a BFS: O(E (V + E)).
2. Improved   — DFS with a single ``visited`` set is WRONG (it reports a cycle for the
   diamond 0->1, 0->2, 1->3, 2->3). We need to distinguish "on the current path" from
   "finished".
3. Optimal    — three-colour DFS: WHITE (unvisited), GRAY (on the recursion stack),
   BLACK (finished). An edge into a GRAY node is a back edge = cycle. O(V + E).
   (Kahn's algorithm, Ex 08, is the BFS alternative: cycle iff not all nodes popped.)
Undirected:
- DFS that ignores the edge back to its parent: any other visited neighbour = cycle.
- Or Union-Find: an edge whose endpoints are already connected closes a cycle.
- Quick check: a connected undirected graph with E >= V has a cycle.

Hints
-----
- Undirected: pass the parent along, or store (node, parent) on the stack.
- Directed: state array with values 0/1/2; set 2 when all children are done.
- Iterative directed DFS: push (node, iterator) pairs so you know when a node finishes.

Follow-ups
----------
- Detect deadlock in a wait-for graph; detect circular imports.
- Find the redundant edge that creates the cycle (Ex 09 Union-Find).
- Return ALL nodes on cycles / eventual safe states (nodes that cannot reach a cycle).
"""
from __future__ import annotations

from collections import deque

WHITE, GRAY, BLACK = 0, 1, 2


def has_cycle_undirected(n: int, edges: list[tuple[int, int]]) -> bool:
    """Iterative DFS remembering each node's parent. O(V + E)."""
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [(s, -1)]
        while stack:
            u, parent = stack.pop()
            for v in adj[u]:
                if v == parent:
                    continue
                if seen[v]:
                    return True
                seen[v] = True
                stack.append((v, u))
    return False


def has_cycle_undirected_dsu(n: int, edges: list[tuple[int, int]]) -> bool:
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            return True
        parent[ru] = rv
    return False


def brute_force(n: int, edges: list[tuple[int, int]]) -> bool:
    """Directed: for each edge u->v check whether v reaches u. O(E (V + E))."""
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    for u, v in edges:
        seen = {v}
        q = deque([v])
        while q:
            x = q.popleft()
            if x == u:
                return True
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    q.append(y)
    return False


def wrong_visited_only(n: int, edges: list[tuple[int, int]]) -> bool:
    """WRONG for directed graphs: 'seen before' is not the same as 'on my path'."""
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    seen = set()
    for s in range(n):
        if s in seen:
            continue
        stack = [s]
        while stack:
            u = stack.pop()
            if u in seen:
                return True
            seen.add(u)
            stack.extend(adj[u])
    return False


def find_cycle(n: int, edges: list[tuple[int, int]]) -> list[int]:
    """Three-colour iterative DFS; reconstructs the cycle from the GRAY path."""
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    state = [WHITE] * n
    for s in range(n):
        if state[s] != WHITE:
            continue
        path = [s]                       # current GRAY path, in order
        state[s] = GRAY
        stack = [(s, iter(adj[s]))]
        while stack:
            u, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:              # all children done -> finish u
                state[u] = BLACK
                stack.pop()
                path.pop()
            elif state[nxt] == GRAY:     # back edge: cycle found
                return path[path.index(nxt):] + [nxt]
            elif state[nxt] == WHITE:
                state[nxt] = GRAY
                path.append(nxt)
                stack.append((nxt, iter(adj[nxt])))
    return []


def solve(n: int, edges: list[tuple[int, int]]) -> bool:
    """Directed cycle detection with three-colour DFS. O(V + E)."""
    return bool(find_cycle(n, edges))


def main() -> None:
    print("undirected:")
    for n, edges in [(3, [(0, 1), (1, 2), (2, 0)]), (4, [(0, 1), (1, 2), (2, 3)]), (4, [(0, 1), (2, 3)])]:
        print(f"  n={n} {edges}: dfs={has_cycle_undirected(n, edges)} dsu={has_cycle_undirected_dsu(n, edges)}")
    print("directed:")
    diamond = [(0, 1), (0, 2), (1, 3), (2, 3)]
    cases = [
        ("diamond (no cycle)", 4, diamond),
        ("1->2->3->1", 4, [(0, 1), (1, 2), (2, 3), (3, 1)]),
        ("self-loop", 2, [(0, 1), (1, 1)]),
        ("two comps", 5, [(0, 1), (2, 3), (3, 4), (4, 2)]),
        ("empty", 0, []),
    ]
    for name, n, edges in cases:
        print(f"  {name:<18} solve={solve(n, edges)!s:<5} brute={brute_force(n, edges)!s:<5} cycle={find_cycle(n, edges)}")
    print("wrong 'visited only' on diamond:", wrong_visited_only(4, diamond), "(should be False)")


if __name__ == "__main__":
    main()
