"""
Exercise 10 — Practice Set: Minimum Arrows, Meeting Rooms, Boats   [Tier: ◆ Extended]
Chapter 20 · Pattern: sort + greedy sweep (mixed practice) · Target time: 30 min

Problem
-------
Three short greedy problems that interviewers like as warm-ups or follow-ups.
1. `min_arrows(balloons)` — balloons are closed intervals [x1, x2] on a line. An arrow shot
   at x bursts every balloon with x1 <= x <= x2. Return the fewest arrows to burst all.
2. `min_rooms(meetings)` — half-open [start, end) meetings; the fewest rooms so that all
   meetings take place.
3. `min_boats(weights, limit)` — each boat carries at most two people with total weight
   <= limit. Return the fewest boats.

Examples
--------
>>> min_arrows([[10, 16], [2, 8], [1, 6], [7, 12]])
2
>>> min_rooms([(0, 30), (5, 10), (15, 20)])
2
>>> min_boats([3, 2, 2, 1], 3)
3

Constraints
-----------
- Up to 10^5 items each; all weights <= limit.

Hints
-----
- Arrows is activity selection in disguise: count a maximal set of pairwise disjoint balloons.
- Rooms: the answer is the maximum number of meetings in progress at any instant.
- Boats: the heaviest person must go with SOMEONE or alone; the lightest is the best partner.

Follow-ups
----------
- Rooms: return which room each meeting uses (heap of (end, room_id)).
- Boats with capacity > 2 people: becomes bin packing, which is NP-hard.
"""
from __future__ import annotations

import heapq


def min_arrows(balloons: list[list[int]]) -> int:
    raise NotImplementedError("TODO")


def min_rooms_brute(meetings: list[tuple[int, int]]) -> int:
    raise NotImplementedError("TODO")


def min_rooms(meetings: list[tuple[int, int]]) -> int:
    raise NotImplementedError("TODO")


def min_boats(weights: list[int], limit: int) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    balloons = [[10, 16], [2, 8], [1, 6], [7, 12]]
    print("balloons", balloons, "-> arrows", min_arrows(balloons))
    print("touching [[1,2],[2,3]] -> arrows", min_arrows([[1, 2], [2, 3]]), "(closed intervals share x=2)")
    print("empty -> arrows", min_arrows([]))
    print()
    for m in ([(0, 30), (5, 10), (15, 20)], [(1, 5), (5, 10)], [(1, 10), (2, 9), (3, 8)], []):
        print(f"meetings {m} -> rooms {min_rooms(m)} (brute {min_rooms_brute(m)})")
    print()
    for w, lim in (([3, 2, 2, 1], 3), ([1, 2], 3), ([3, 5, 3, 4], 5), ([5, 1, 4, 2], 6)):
        print(f"weights {w} limit {lim} -> boats {min_boats(w, lim)}")


if __name__ == "__main__":
    main()
