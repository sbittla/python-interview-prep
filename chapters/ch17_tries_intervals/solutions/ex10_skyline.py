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

Approach ladder
---------------
1. Brute force — for every critical x (all edges), take the max height of buildings with
   left <= x < right; emit when it changes. O(n) per x, O(n^2) total.
2. Optimal    — sort the 2n edges; maintain a max-heap of active buildings with lazy deletion.
   Each building is pushed and popped at most once: O(n log n) time, O(n) space.
   Why move up: rung 1 rescans every building at every edge; the heap answers
   "tallest active building" in O(1) after amortised O(log n) maintenance.

Wrong-but-tempting
------------------
- Emitting a point per event instead of per x: equal-x starts/ends produce [x, a], [x, b]
  pairs, and adjacent buildings of equal height produce a redundant point.
- Removing an ended building from the middle of the heap with list.remove: O(n) per removal.
- Treating right edges as inclusive: (0, 2, 3), (2, 5, 1) would report height 3 at x = 2.

Follow-ups
----------
- Maximum number of overlapping intervals and where (Ex 09 busiest): same sweep, counter
  instead of heap.
- Area of the union of rectangles: sweep plus a segment tree over y.
"""
from __future__ import annotations

import heapq


def brute_force(buildings: list[tuple[int, int, int]]) -> list[list[int]]:
    out: list[list[int]] = []
    for x in sorted({b[0] for b in buildings} | {b[1] for b in buildings}):
        h = max((bh for l, r, bh in buildings if l <= x < r), default=0)
        if not out or out[-1][1] != h:
            out.append([x, h])
    return out


def solve(buildings: list[tuple[int, int, int]]) -> list[list[int]]:
    xs = sorted({b[0] for b in buildings} | {b[1] for b in buildings})
    by_left = sorted(buildings)
    heap: list[tuple[int, int]] = []          # (-height, right) of started buildings
    out: list[list[int]] = []
    i = 0
    for x in xs:
        while i < len(by_left) and by_left[i][0] == x:      # all starts at this x
            _, right, h = by_left[i]
            heapq.heappush(heap, (-h, right))
            i += 1
        while heap and heap[0][1] <= x:                      # lazy deletion of ended tops
            heapq.heappop(heap)
        h = -heap[0][0] if heap else 0
        if not out or out[-1][1] != h:                       # emit only on a change
            out.append([x, h])
    return out


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
