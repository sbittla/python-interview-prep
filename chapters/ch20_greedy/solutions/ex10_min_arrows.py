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

Approach ladder
---------------
1. Arrows — brute force tries arrow positions at every endpoint subset (exponential). Greedy:
   sort by right end, shoot at the right end of the first unburst balloon; it bursts every
   balloon that starts at or before that point. O(n log n).
2. Rooms — brute force checks every time point for the maximum overlap, O(n * range). Sweep:
   sort starts and ends separately and walk both, or keep a min-heap of end times.
   O(n log n).
3. Boats — brute force tries all pairings. Greedy two pointers: pair the heaviest with the
   lightest if they fit, otherwise the heaviest goes alone. O(n log n).

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
    arrows = 0
    arrow_x = float("-inf")
    for x1, x2 in sorted(balloons, key=lambda b: b[1]):
        if x1 > arrow_x:              # current arrow misses this balloon
            arrows += 1
            arrow_x = x2              # shoot as far right as possible
    return arrows


def min_rooms_brute(meetings: list[tuple[int, int]]) -> int:
    if not meetings:
        return 0
    lo = min(s for s, _ in meetings)
    hi = max(e for _, e in meetings)
    return max(sum(1 for s, e in meetings if s <= t < e) for t in range(lo, hi))


def min_rooms(meetings: list[tuple[int, int]]) -> int:
    ends: list[int] = []              # min-heap of end times of rooms in use
    for start, end in sorted(meetings):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)   # reuse the room that frees up first
        else:
            heapq.heappush(ends, end)
    return len(ends)


def min_boats(weights: list[int], limit: int) -> int:
    w = sorted(weights)
    i, j = 0, len(w) - 1
    boats = 0
    while i <= j:
        if w[i] + w[j] <= limit:
            i += 1                    # lightest rides with the heaviest
        j -= 1                        # heaviest always leaves now
        boats += 1
    return boats


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
