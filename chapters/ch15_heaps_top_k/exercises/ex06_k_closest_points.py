"""
Exercise 06 — K Closest Points to a Target                         [Tier: ★ Core]
Chapter 15 · Pattern: size-k max-heap on distance · Target time: 15 min

Problem
-------
Given integer points (x, y), an integer target point (default the origin) and k, return the
k points closest to the target by Euclidean distance, ordered nearest first. Ties on
distance are broken by (x, y) ascending, so the answer is unique. Duplicate points count
separately.

Examples
--------
>>> solve([(1, 3), (-2, 2), (2, -2)], 2)
[(-2, 2), (2, -2)]
>>> solve([(0, 5), (3, 4), (5, 0)], 1, target=(3, 3))
[(3, 4)]

Constraints
-----------
- 0 <= k <= len(points) <= 10^5; coordinates are ints.

Hints
-----
- Compare squared distances: no sqrt, no floats, exact ties.
- Negating every key component turns heapq's min-heap into a max-heap over the full key.

Follow-ups
----------
- Points arrive as a stream and the client asks for the current k nearest at any time:
  only the size-k heap works.
- Float coordinates: squared distances can tie or not depending on rounding; state the
  tie rule explicitly.
- Many queries with different targets: a k-d tree (name it; rarely coded).

Wrong-but-tempting
------------------
- Size-k MIN-heap on distance: its root is the nearest point, so popping it throws away
  the best answer.
- `math.dist` / `sqrt` for ranking: correct order but slower and float-equal ties wobble.
"""
from __future__ import annotations

import heapq
import random

Point = tuple[int, int]


def _key(p: Point, target: Point) -> tuple[int, int, int]:
    raise NotImplementedError("TODO")


def brute_force(points: list[Point], k: int, target: Point = (0, 0)) -> list[Point]:
    raise NotImplementedError("TODO")


def by_nsmallest(points: list[Point], k: int, target: Point = (0, 0)) -> list[Point]:
    raise NotImplementedError("TODO")


def by_max_heap(points: list[Point], k: int, target: Point = (0, 0)) -> list[Point]:
    raise NotImplementedError("TODO")


def solve(points: list[Point], k: int, target: Point = (0, 0)) -> list[Point]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [([(1, 3), (-2, 2), (2, -2)], 2, (0, 0)),
             ([(0, 5), (3, 4), (5, 0)], 1, (3, 3)),
             ([(1, 0), (0, 1), (-1, 0), (0, -1)], 3, (0, 0)),
             ([(2, 2), (2, 2), (1, 1)], 2, (0, 0)),
             ([(4, 4)], 0, (0, 0))]
    for pts, k, t in cases:
        ans = solve(pts, k, t)
        agree = ans == brute_force(pts, k, t) == by_nsmallest(pts, k, t)
        print(f"k={k} target={t} {pts} -> {ans}  agree={agree}")
    rng = random.Random(15)
    ok = True
    for _ in range(300):
        pts = [(rng.randint(-3, 3), rng.randint(-3, 3)) for _ in range(rng.randint(0, 20))]
        k = rng.randint(0, len(pts))
        t = (rng.randint(-2, 2), rng.randint(-2, 2))
        ok &= solve(pts, k, t) == brute_force(pts, k, t) == by_nsmallest(pts, k, t)
    print("300 random tie-heavy cases agree:", ok)


if __name__ == "__main__":
    main()
