"""
Exercise 05 — Multi-Source BFS: Rotting Oranges, Distance to Nearest   [Tier: ★ Core]
Chapter 16 · Pattern: multi-source BFS · Target time: 20 min

Problem
-------
(a) ``solve(grid)``: a grid holds 0 (empty), 1 (fresh orange) and 2 (rotten orange).
Each minute every rotten orange rots its fresh 4-neighbours. Return the minutes until
no fresh orange remains, or -1 if some fresh orange can never rot. 0 if none are fresh.

(b) ``nearest_zero(mat)``: for a 0/1 matrix, return a matrix where each cell holds the
Manhattan-step distance (4-directional moves) to the nearest 0. At least one 0 exists.

Examples
--------
>>> solve([[2, 1, 1], [1, 1, 0], [0, 1, 1]])
4
>>> solve([[2, 1, 1], [0, 1, 1], [1, 0, 1]])
-1
>>> nearest_zero([[0, 0, 0], [0, 1, 0], [1, 1, 1]])
[[0, 0, 0], [0, 1, 0], [1, 2, 1]]

Constraints
-----------
- 1 <= rows, cols <= 200 (part b up to 10**4 cells).

Approach ladder
---------------
1. Brute force — simulate minute by minute: scan the whole grid, rot neighbours of
   rotten cells into a copy, repeat until nothing changes. O((RC)^2) worst case
   (a long snake of oranges rots one cell per minute, each minute rescans RC cells).
   For (b): BFS from every 1-cell separately: O((RC)^2).
2. Improved   — BFS from each rotten orange separately, take per-cell minimum:
   O(k * RC) for k sources.
3. Optimal    — put ALL sources in the queue at distance 0 and run one BFS. It is
   as if a virtual super-source connects to every source with a 0-cost edge.
   O(RC) time and space. Layers of this BFS are exactly the minutes.

Hints
-----
- Count fresh oranges up front; decrement when one rots; answer -1 if any remain.
- Process the queue level by level to count minutes, or store (r, c, t) tuples.
- For (b), seed the queue with every 0 and treat 1-cells as "unvisited" (dist = -1).

Follow-ups
----------
- Walls and gates (distance from every room to the nearest gate) — same template.
- Shortest distance from all buildings (sum over sources) — NOT multi-source; BFS per building.
- As far from land as possible (max over the multi-source distance map).
"""
from __future__ import annotations

from collections import deque

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def brute_force(grid: list[list[int]]) -> int:
    """Minute-by-minute full-grid simulation. O((RC)^2) worst case."""
    g = [row[:] for row in grid]
    rows, cols = len(g), len(g[0])
    minutes = 0
    while True:
        nxt = [row[:] for row in g]
        changed = False
        for r in range(rows):
            for c in range(cols):
                if g[r][c] == 2:
                    for dr, dc in DIRS:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and nxt[nr][nc] == 1:
                            nxt[nr][nc] = 2
                            changed = True
        if not changed:
            break
        g = nxt
        minutes += 1
    if any(1 in row for row in g):
        return -1
    return minutes


def rot_trace(grid: list[list[int]]) -> list[list[list[int]]]:
    """Multi-source BFS returning a snapshot of the grid after each minute."""
    g = [row[:] for row in grid]
    rows, cols = len(g), len(g[0])
    q = deque((r, c) for r in range(rows) for c in range(cols) if g[r][c] == 2)
    snapshots = [[row[:] for row in g]]
    while q:
        rotted = False
        for _ in range(len(q)):
            r, c = q.popleft()
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == 1:
                    g[nr][nc] = 2
                    q.append((nr, nc))
                    rotted = True
        if rotted:
            snapshots.append([row[:] for row in g])
    return snapshots


def solve(grid: list[list[int]]) -> int:
    """One BFS seeded with every rotten orange. O(RC)."""
    rows, cols = len(grid), len(grid[0])
    g = [row[:] for row in grid]
    q = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == 2:
                q.append((r, c))
            elif g[r][c] == 1:
                fresh += 1
    minutes = 0
    while q and fresh:
        minutes += 1
        for _ in range(len(q)):             # one BFS layer == one minute
            r, c = q.popleft()
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == 1:
                    g[nr][nc] = 2
                    fresh -= 1
                    q.append((nr, nc))
    return -1 if fresh else minutes


def nearest_zero_brute(mat: list[list[int]]) -> list[list[int]]:
    """Separate BFS from every cell to its nearest 0. O((RC)^2)."""
    rows, cols = len(mat), len(mat[0])
    out = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == 0:
                continue
            seen = {(r, c)}
            q = deque([(r, c, 0)])
            while q:
                cr, cc, d = q.popleft()
                if mat[cr][cc] == 0:
                    out[r][c] = d
                    break
                for dr, dc in DIRS:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        q.append((nr, nc, d + 1))
    return out


def nearest_zero(mat: list[list[int]]) -> list[list[int]]:
    """Multi-source BFS from every 0 at once. O(RC)."""
    rows, cols = len(mat), len(mat[0])
    dist = [[-1] * cols for _ in range(rows)]
    q = deque()
    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == 0:
                dist[r][c] = 0
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist


def show(grid: list[list[int]], symbols: str = ".oX") -> str:  # keep
    return "\n".join("  " + " ".join(symbols[v] for v in row) for row in grid)


def main() -> None:
    grid = [[2, 1, 1], [1, 1, 0], [0, 1, 1]]
    print("legend: . empty, o fresh, X rotten")
    for minute, snap in enumerate(rot_trace(grid)):
        print(f"minute {minute}:")
        print(show(snap))
    print("solve =", solve(grid), "| brute =", brute_force(grid))
    for g in [[[2, 1, 1], [0, 1, 1], [1, 0, 1]], [[0, 2]], [[1]], [[2, 2], [1, 1]], [[0]]]:
        print(f"{g!s:<32} -> {solve(g)} (brute {brute_force(g)})")
    mat = [[0, 0, 0], [0, 1, 0], [1, 1, 1]]
    print("nearest_zero:", nearest_zero(mat), "matches brute:", nearest_zero(mat) == nearest_zero_brute(mat))
    mat2 = [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0]]
    print("distance map:")
    for row in nearest_zero(mat2):
        print("  " + " ".join(map(str, row)))


if __name__ == "__main__":
    main()
