"""
Exercise 04 — Number of Islands and Flood Fill          [Tier: ★ Core]
Chapter 16 · Pattern: grid DFS/BFS · Target time: 15 min

Problem
-------
A map is a list of strings of '1' (land) and '0' (water). An island is a maximal group
of land cells connected up/down/left/right. ``solve(grid)`` returns the number of
islands. ``label_islands(grid)`` returns a copy where each island's cells are replaced
by a letter A, B, C ... in discovery order (row-major scan). ``flood_fill(image, r, c,
new)`` recolours the 4-connected region containing (r, c) and returns a new image.

Examples
--------
>>> solve(["110", "010", "001"])
2
>>> flood_fill([[1, 1, 0], [1, 0, 0]], 0, 0, 7)
[[7, 7, 0], [7, 0, 0]]

Constraints
-----------
- 0 <= rows, cols <= 300. Diagonal cells are NOT connected.
- Do not mutate the caller's grid.

Approach ladder
---------------
1. Brute force — BFS from EVERY land cell, record the island it reaches as a frozenset,
   and count distinct sets: O((RC)^2), because each island is re-explored once per cell.
   (Union-Find over land cells is also valid, O(RC α(RC)), but more machinery.)
2. Improved   — recursive DFS flood fill from each unvisited land cell: O(RC), but a
   300x300 all-land grid recurses 90,000 deep -> RecursionError.
3. Optimal    — iterative BFS/DFS with a queue/stack, marking cells when pushed:
   O(RC) time, O(min(R, C)) to O(RC) queue space, no recursion limit.

Hints
-----
- Copy the grid into a list of lists of chars so you can mark visited cells in place.
- Scan row-major; every unvisited '1' starts a new island.
- Flood fill: if the new colour equals the old colour, return immediately (else an
  in-place version loops forever / does useless work).

Follow-ups
----------
- Max area of an island; perimeter of an island.
- Number of distinct island shapes (normalise relative coordinates).
- Islands added one at a time (Number of Islands II) -> Union-Find.
- Count closed islands / surrounded regions: flood from the border first.
"""
from __future__ import annotations

from collections import deque

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def brute_force(grid: list[str]) -> int:
    """BFS from EVERY land cell, collect each island as a frozenset, dedupe."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    islands = set()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1":
                continue
            seen = {(r, c)}
            q = deque([(r, c)])
            while q:
                cr, cc = q.popleft()
                for dr, dc in DIRS:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1" and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        q.append((nr, nc))
            islands.add(frozenset(seen))
    return len(islands)


def dfs_recursive(grid: list[str]) -> int:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    g = [list(row) for row in grid]

    def sink(r: int, c: int) -> None:
        if not (0 <= r < rows and 0 <= c < cols) or g[r][c] != "1":
            return
        g[r][c] = "0"
        for dr, dc in DIRS:
            sink(r + dr, c + dc)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == "1":
                count += 1
                sink(r, c)
    return count


def label_islands(grid: list[str]) -> list[str]:
    """Iterative BFS; each island gets the next letter. O(RC)."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    g = [list(row) for row in grid]
    label = 0
    for r in range(rows):
        for c in range(cols):
            if g[r][c] != "1":
                continue
            mark = chr(ord("A") + label % 26)
            label += 1
            g[r][c] = mark                     # mark on push
            q = deque([(r, c)])
            while q:
                cr, cc = q.popleft()
                for dr, dc in DIRS:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == "1":
                        g[nr][nc] = mark
                        q.append((nr, nc))
    return ["".join(row) for row in g]


def solve(grid: list[str]) -> int:
    """Iterative DFS with an explicit stack and a seen matrix. O(RC)."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    seen = [[False] * cols for _ in range(rows)]
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1" or seen[r][c]:
                continue
            count += 1
            seen[r][c] = True
            stack = [(r, c)]
            while stack:
                cr, cc = stack.pop()
                for dr, dc in DIRS:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1" and not seen[nr][nc]:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
    return count


def flood_fill(image: list[list[int]], r: int, c: int, new: int) -> list[list[int]]:
    img = [row[:] for row in image]
    old = img[r][c]
    if old == new:
        return img
    img[r][c] = new
    stack = [(r, c)]
    while stack:
        cr, cc = stack.pop()
        for dr, dc in DIRS:
            nr, nc = cr + dr, cc + dc
            if 0 <= nr < len(img) and 0 <= nc < len(img[0]) and img[nr][nc] == old:
                img[nr][nc] = new
                stack.append((nr, nc))
    return img


def main() -> None:
    grid = [
        "11000",
        "11010",
        "00100",
        "00011",
        "10011",
    ]
    print("input grid:")
    for row in grid:
        print("  " + row)
    print("labelled islands:")
    for row in label_islands(grid):
        print("  " + row)
    print("islands =", solve(grid), "| brute =", brute_force(grid), "| recursive =", dfs_recursive(grid))
    for g in [[], ["0"], ["1"], ["101", "010", "101"], ["111", "101", "111"]]:
        print(f"{g!s:<24} -> {solve(g)}")
    big = ["1" * 300] * 300
    try:
        dfs_recursive(big)
        print("recursive on 300x300 land: ok")
    except RecursionError:
        print("recursive on 300x300 land: RecursionError")
    print("iterative on 300x300 land:", solve(big))
    image = [[1, 1, 1], [1, 1, 0], [1, 0, 1]]
    print("flood_fill from (1,1) with 2:", flood_fill(image, 1, 1, 2))
    print("flood_fill same colour      :", flood_fill(image, 0, 0, 1))


if __name__ == "__main__":
    main()
