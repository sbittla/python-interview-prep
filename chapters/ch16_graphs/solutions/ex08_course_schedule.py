"""
Exercise 08 — Course Schedule (Topological Sort)        [Tier: ★ Core]
Chapter 16 · Pattern: Kahn's algorithm / DFS post-order · Target time: 20 min

Problem
-------
There are ``n`` courses 0..n-1. ``prereqs`` holds pairs (course, before) meaning
``before`` must be taken before ``course``. ``solve(n, prereqs)`` returns an order in
which all courses can be taken, or [] if impossible (a cycle). Use Kahn's algorithm,
seeding and appending zero-in-degree nodes in increasing node order (a FIFO queue), so
the output is deterministic. ``can_finish`` returns a bool. ``topo_dfs`` returns a
valid order using DFS post-order.

Examples
--------
>>> solve(4, [(1, 0), (2, 0), (3, 1), (3, 2)])
[0, 1, 2, 3]
>>> solve(2, [(0, 1), (1, 0)])
[]

Constraints
-----------
- 1 <= n <= 2000, 0 <= len(prereqs) <= 5000.

Approach ladder
---------------
1. Brute force — repeatedly scan all remaining courses for one whose prerequisites are
   all taken; take it. O(V * (V + E)). If a scan finds nothing, there is a cycle.
2. Improved   — DFS post-order (three-colour, so cycles are detected) and reverse:
   O(V + E). Correct, but recursion depth can hit the limit, and order is less intuitive.
3. Optimal    — Kahn's algorithm: compute in-degrees, queue every 0-in-degree node, pop,
   "remove" its out-edges by decrementing in-degrees, enqueue nodes that reach 0.
   O(V + E), iterative, and the cycle test is free: popped count < n.

Hints
-----
- Edge direction: before -> course. Getting this backwards reverses the order.
- Kahn: ``order`` length != n means a cycle.
- DFS: append a node AFTER all its descendants, then reverse the list.
- Want the lexicographically smallest order? Replace the deque with a min-heap.

Follow-ups
----------
- Minimum number of semesters (parallel courses) = number of Kahn layers.
- Alien dictionary (Ex 18): build edges from adjacent word pairs, then topo sort.
- Build systems, package installation, spreadsheet recalculation.
"""
from __future__ import annotations

import sys
from collections import deque


def brute_force(n: int, prereqs: list[tuple[int, int]]) -> list[int]:
    """Repeated scans for an available course. O(V * (V + E))."""
    needs: list[set[int]] = [set() for _ in range(n)]
    for course, before in prereqs:
        needs[course].add(before)
    taken: set[int] = set()
    order = []
    while len(order) < n:
        for c in range(n):
            if c not in taken and needs[c] <= taken:
                taken.add(c)
                order.append(c)
                break
        else:
            return []                    # nothing available: cycle
    return order


def topo_dfs(n: int, prereqs: list[tuple[int, int]]) -> list[int]:
    """Reverse DFS post-order with cycle detection. O(V + E)."""
    adj: list[list[int]] = [[] for _ in range(n)]
    for course, before in prereqs:
        adj[before].append(course)
    state = [0] * n                      # 0 white, 1 gray, 2 black
    post: list[int] = []
    sys.setrecursionlimit(max(10_000, sys.getrecursionlimit()))

    def dfs(u: int) -> bool:
        state[u] = 1
        for v in adj[u]:
            if state[v] == 1:
                return False             # back edge
            if state[v] == 0 and not dfs(v):
                return False
        state[u] = 2
        post.append(u)                   # all descendants are already in post
        return True

    for u in range(n):
        if state[u] == 0 and not dfs(u):
            return []
    return post[::-1]


def kahn_trace(n: int, prereqs: list[tuple[int, int]]) -> tuple[list[int], list[str]]:
    adj: list[list[int]] = [[] for _ in range(n)]
    indeg = [0] * n
    for course, before in prereqs:
        adj[before].append(course)
        indeg[course] += 1
    q = deque(u for u in range(n) if indeg[u] == 0)
    order, log = [], [f"start   indeg={indeg} queue={list(q)}"]
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
        log.append(f"pop {u:<3} indeg={indeg} queue={list(q)}")
    return (order if len(order) == n else []), log


def solve(n: int, prereqs: list[tuple[int, int]]) -> list[int]:
    """Kahn's algorithm. O(V + E)."""
    adj: list[list[int]] = [[] for _ in range(n)]
    indeg = [0] * n
    for course, before in prereqs:
        adj[before].append(course)       # edge: before -> course
        indeg[course] += 1
    q = deque(u for u in range(n) if indeg[u] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else []


def can_finish(n: int, prereqs: list[tuple[int, int]]) -> bool:
    return len(solve(n, prereqs)) == n


def is_valid_order(n: int, prereqs: list[tuple[int, int]], order: list[int]) -> bool:  # keep
    pos = {c: i for i, c in enumerate(order)}
    return len(order) == n and all(pos[b] < pos[c] for c, b in prereqs)


def main() -> None:
    n, pre = 6, [(1, 0), (2, 0), (3, 1), (3, 2), (4, 3), (5, 3)]
    print("edges (before -> course):", sorted((b, c) for c, b in pre))
    order, log = kahn_trace(n, pre)
    print("Kahn trace:")
    for line in log:
        print("  " + line)
    print("kahn  :", order)
    print("dfs   :", topo_dfs(n, pre), "valid:", is_valid_order(n, pre, topo_dfs(n, pre)))
    print("brute :", brute_force(n, pre))
    cyc = [(0, 1), (1, 2), (2, 0)]
    print("cycle :", solve(3, cyc), topo_dfs(3, cyc), brute_force(3, cyc), "can_finish:", can_finish(3, cyc))
    print("no prereqs:", solve(3, []))


if __name__ == "__main__":
    main()
