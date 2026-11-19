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
    raise NotImplementedError("TODO")


def tsp_memo(dist: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def tsp(dist: list[list[int]]) -> tuple[int, list[int]]:
    raise NotImplementedError("TODO")


def tsp_cost(dist: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


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
