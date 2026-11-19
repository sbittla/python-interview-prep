"""
Exercise 10 — The skyline (line sweep + max-heap)                [Tier: ◆ Extended]
Chapter 17 · Pattern: sweep over x with a lazily-cleaned max-heap · Target time: 40 min

Problem
-------
Each building is (left, right, height) with left < right and height > 0; it covers the
half-open x-range [left, right). The skyline is the outline of the union: a list of key points
[x, h] meaning "from x onwards the outline is at height h", sorted by x, with no two
consecutive points at the same height, ending with a point at height 0.

Examples
--------
>>> solve([(2, 9, 10), (3, 7, 15), (5, 12, 12), (15, 20, 10), (19, 24, 8)])
[[2, 10], [3, 15], [7, 12], [12, 0], [15, 10], [20, 8], [24, 0]]
>>> solve([(0, 2, 3), (2, 5, 3)])
[[0, 3], [5, 0]]
>>> solve([])
[]

Constraints
-----------
- 0 <= n <= 10^4; integer coordinates.

Hints
-----
- The outline can only change at a left or right edge, so sweep those x values in order.
- Keep the buildings that have started in a max-heap keyed by height (store -height with
  heapq). Do not delete a building when it ends; instead, pop from the top while the top's
  right edge is <= the current x ("lazy deletion").
- Process all events at one x before emitting a point, and emit only when the height changes.

Follow-ups
----------
- Maximum number of overlapping intervals and where (Ex 09 busiest): same sweep, counter
  instead of heap.
- Area of the union of rectangles: sweep plus a segment tree over y.
"""
from __future__ import annotations

import heapq


def brute_force(buildings: list[tuple[int, int, int]]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def solve(buildings: list[tuple[int, int, int]]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def main() -> None:
    city = [(2, 9, 10), (3, 7, 15), (5, 12, 12), (15, 20, 10), (19, 24, 8)]
    print("skyline:", solve(city))
    print("brute  :", brute_force(city))
    print("equal-height neighbours:", solve([(0, 2, 3), (2, 5, 3)]))
    print("right edge is exclusive:", solve([(0, 2, 3), (2, 5, 1)]))
    print("same left, nested      :", solve([(1, 5, 2), (1, 3, 4)]))
    print("empty                  :", solve([]))


if __name__ == "__main__":
    main()
