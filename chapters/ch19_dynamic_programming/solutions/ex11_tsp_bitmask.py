"""
Exercise 11 — Shortest Round Trip (TSP-lite, bitmask DP)            [Tier: ◆ Extended]
Chapter 19 · Pattern: bitmask DP over subsets · Target time: 40 min

Problem
-------
dist[i][j] >= 0 is the cost of travelling from city i to city j (it need not be
symmetric). Starting and ending at city 0, visit every other city exactly once.
`tsp_cost(dist)` returns the cheapest tour cost; `tsp(dist)` also returns one optimal
tour as a list of cities that starts and ends with 0. One city: cost 0, tour [0, 0].

Examples
--------
>>> d = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
>>> tsp(d)
(80, [0, 2, 3, 1, 0])

Constraints
-----------
- 1 <= n <= 15 (2^15 * 15 = 491,520 states).

Approach ladder
---------------
Recipe — state: dp[mask][j] = cheapest path that starts at 0, visits exactly the
cities in mask (which contains 0 and j), and ends at j; transition: dp[mask][j] =
min(dp[mask without j][i] + dist[i][j]) over i in mask - {j}; base: dp[{0}][0] = 0;
order: masks in increasing numeric order (a subset is always numerically smaller
than any superset); answer: min(dp[full][j] + dist[j][0]).
1. Plain recursion over orders (= itertools.permutations of cities 1..n-1):
   O(n!) time. n = 12 is already ~40 million tours.
2. Memoised f(mask, last) — the cost of FINISHING depends only on which cities are
   visited and where you stand, not on the order you visited them: O(2^n * n) states,
   O(n) work each: O(2^n * n^2) time, O(2^n * n) space.
3. Bottom-up table with a parent table for the tour: same bounds.
   No rolling array: a mask reads masks with one bit fewer, scattered across the table.

Hints
-----
- Bit tricks: mask >> j & 1 tests city j; mask | 1 << j adds it; mask ^ 1 << j removes it.
- Skip masks that do not contain city 0 — they are unreachable.

Follow-ups
----------
- Shortest path visiting all nodes of an unweighted graph: BFS over (node, mask).
- Assignment problems ("n workers, n jobs"): dp[mask] where popcount(mask) = next worker.
"""
from __future__ import annotations

from functools import cache
from itertools import permutations


def tsp_brute(dist: list[list[int]]) -> int:
    n = len(dist)
    best = float("inf")
    for order in permutations(range(1, n)):
        tour = (0, *order, 0)
        best = min(best, sum(dist[a][b] for a, b in zip(tour, tour[1:])))
    return int(best)


def tsp_memo(dist: list[list[int]]) -> int:
    n = len(dist)
    full = (1 << n) - 1

    @cache
    def finish(mask: int, last: int) -> int:    # cheapest way to visit the rest and return
        if mask == full:
            return dist[last][0]
        return min(dist[last][nxt] + finish(mask | 1 << nxt, nxt)
                   for nxt in range(n) if not mask >> nxt & 1)

    return finish(1, 0)


def tsp(dist: list[list[int]]) -> tuple[int, list[int]]:
    n = len(dist)
    if n == 1:
        return 0, [0, 0]
    inf = float("inf")
    full = (1 << n) - 1
    dp = [[inf] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]
    dp[1][0] = 0
    for mask in range(1, 1 << n):
        if not mask & 1:
            continue                            # every path starts at city 0
        for j in range(n):
            if dp[mask][j] == inf:
                continue
            for k in range(n):                  # extend the path from j to a new city k
                if mask >> k & 1:
                    continue
                nxt = mask | 1 << k
                cand = dp[mask][j] + dist[j][k]
                if cand < dp[nxt][k]:
                    dp[nxt][k], parent[nxt][k] = cand, j
    cost, last = min((dp[full][j] + dist[j][0], j) for j in range(1, n))
    tour, mask = [0], full
    while last != 0:
        tour.append(last)
        mask, last = mask ^ 1 << last, parent[mask][last]
    tour.append(0)
    return int(cost), tour[::-1]


def tsp_cost(dist: list[list[int]]) -> int:
    return tsp(dist)[0]


def main() -> None:
    d = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
    print("4 cities:", tsp(d), "brute:", tsp_brute(d), "memo:", tsp_memo(d))
    one_way = [[0, 1, 9], [9, 0, 1], [1, 9, 0]]          # asymmetric: 0->1->2->0 is cheap
    print("asymmetric 3 cities:", tsp(one_way), "brute:", tsp_brute(one_way))
    print("1 city:", tsp([[0]]), " 2 cities:", tsp([[0, 4], [6, 0]]))
    n = 13
    big = [[0 if i == j else (i * 31 + j * 17) % 50 + 1 for j in range(n)] for i in range(n)]
    cost, tour = tsp(big)
    print(f"{n} cities: cost {cost}, tour visits each once: {sorted(tour[1:]) == list(range(n))}")


if __name__ == "__main__":
    main()
