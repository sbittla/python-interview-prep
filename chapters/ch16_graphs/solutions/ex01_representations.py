"""
Exercise 01 — Graph Representations                     [Tier: ★ Core]
Chapter 16 · Pattern: build adjacency list / matrix / implicit grid · Target time: 10 min

Problem
-------
Graphs arrive in interviews in four shapes: an edge list, an adjacency list, an
adjacency matrix, or an implicit grid where cells are nodes. Write converters:

- ``to_adj_list(n, edges, directed=False)`` -> dict node -> sorted neighbour list
  (every node 0..n-1 present, even if isolated).
- ``to_matrix(n, edges, directed=False)`` -> n x n list of 0/1.
- ``matrix_to_edges(matrix, directed=False)`` -> sorted edge list (u < v when undirected).
- ``grid_neighbors(grid, r, c)`` -> in-bounds 4-directional neighbours, in the
  fixed order up, down, left, right.

Examples
--------
>>> to_adj_list(4, [(0, 1), (1, 2)])
{0: [1], 1: [0, 2], 2: [1], 3: []}
>>> grid_neighbors(["ab", "cd"], 0, 0)
[(1, 0), (0, 1)]

Constraints
-----------
- 0 <= n <= 10**4, edges are pairs of ints in [0, n).
- Grid is a list of equal-length strings or lists.

Approach ladder
---------------
1. Brute force — answer "is u adjacent to v?" by scanning the edge list: O(E) per query.
2. Improved   — adjacency matrix: O(1) edge query, but O(V^2) memory and O(V) to list
   neighbours. Good only for dense graphs (E close to V^2) or Floyd-Warshall.
3. Optimal    — adjacency list (dict of lists / defaultdict(list)): O(V + E) memory,
   neighbour iteration proportional to degree. This is what BFS/DFS want, so it is the
   default. Grids need no conversion: neighbours are computed on the fly.

Hints
-----
- Undirected edge (u, v) must be added in both directions.
- Initialise every node so isolated vertices are not lost.
- Keep a DIRS constant for grids and bounds-check with 0 <= nr < rows.

Follow-ups
----------
- Weighted edges: store (neighbour, weight) tuples.
- Very sparse huge graph given as a function: never materialise it (implicit graph).
- 8-directional grids, knight moves: just change DIRS.
"""
from __future__ import annotations

from collections import defaultdict

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right


def has_edge_scan(edges: list[tuple[int, int]], u: int, v: int, directed: bool = False) -> bool:
    """Brute force: O(E) scan of the edge list per query."""
    for a, b in edges:
        if (a, b) == (u, v) or (not directed and (b, a) == (u, v)):
            return True
    return False


def to_matrix(n: int, edges: list[tuple[int, int]], directed: bool = False) -> list[list[int]]:
    """O(V^2) memory, O(1) edge query."""
    m = [[0] * n for _ in range(n)]
    for u, v in edges:
        m[u][v] = 1
        if not directed:
            m[v][u] = 1
    return m


def matrix_to_edges(matrix: list[list[int]], directed: bool = False) -> list[tuple[int, int]]:
    n = len(matrix)
    out = []
    for u in range(n):
        for v in range(n):
            if matrix[u][v] and (directed or u < v):
                out.append((u, v))
    return out


def to_adj_list(n: int, edges: list[tuple[int, int]], directed: bool = False) -> dict[int, list[int]]:
    """O(V + E): the default representation for traversal."""
    adj: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        if not directed:
            adj[v].append(u)
    return {node: sorted(adj[node]) for node in range(n)}


def grid_neighbors(grid, r: int, c: int) -> list[tuple[int, int]]:
    rows, cols = len(grid), len(grid[0])
    out = []
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            out.append((nr, nc))
    return out


def solve(n: int, edges: list[tuple[int, int]], directed: bool = False) -> dict[int, list[int]]:
    return to_adj_list(n, edges, directed)


def main() -> None:
    n, edges = 5, [(0, 1), (0, 2), (1, 2), (2, 3)]
    print("edge list   :", edges, "(node 4 is isolated)")
    print("adj list    :", to_adj_list(n, edges))
    print("directed    :", to_adj_list(n, edges, directed=True))
    print("matrix:")
    print("     " + " ".join(str(c) for c in range(n)))
    for i, row in enumerate(to_matrix(n, edges)):
        print(f"  {i} [" + " ".join(map(str, row)) + "]")
    print("matrix -> edges:", matrix_to_edges(to_matrix(n, edges)))
    print("has_edge_scan(2, 1):", has_edge_scan(edges, 2, 1), "| directed:", has_edge_scan(edges, 2, 1, True))
    grid = ["S.#", "..#", "#.E"]
    print("grid:")
    for row in grid:
        print("  " + row)
    for cell in [(0, 0), (1, 1), (2, 2)]:
        print(f"neighbours of {cell}: {grid_neighbors(grid, *cell)}")
    print("empty graph:", to_adj_list(0, []))


if __name__ == "__main__":
    main()
