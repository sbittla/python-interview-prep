"""
Exercise 07 — Largest Rectangle in a Histogram               [Tier: ★ Core]
Chapter 12 · Pattern: monotonic stack (previous/next smaller) · Target time: 30 min

Problem
-------
``heights[i]`` is the height of a bar of width 1. Return the area of the largest axis-aligned
rectangle that fits entirely inside the histogram.

Examples
--------
>>> largest_rectangle([2, 1, 5, 6, 2, 3])
10
>>> largest_rectangle([2, 4])
4

Constraints
-----------
- 0 <= len(heights) <= 10**5; 0 <= heights[i] <= 10**4.

Hints
-----
- For each bar as the shortest bar, how far can the rectangle extend left and right?
- Those limits are the previous and next *smaller* bars (monotonic stack).
- One pass: compute a bar's area when it is popped; a sentinel 0 flushes the stack.

Wrong-but-tempting
------------------
- Width ``i - top`` instead of ``i - new_top - 1``: the rectangle extends left past the
  popped bar to the previous smaller bar, not just to the popped bar itself.
- Forgetting to flush the stack at the end: an increasing histogram never pops otherwise.
- Greedy "expand around the tallest bar": the answer is often a wide, low rectangle.

Follow-ups
----------
- Maximal rectangle of 1s in a binary matrix: treat each row as a histogram of column
  heights and call this function per row. O(rows * cols).
- Equal heights: the strict ``>`` vs ``>=`` choice only changes which index computes the
  area; the maximum is the same either way.
"""
from __future__ import annotations


def brute_force(heights: list[int]) -> int:
    raise NotImplementedError("TODO")


def with_boundaries(heights: list[int]) -> int:
    raise NotImplementedError("TODO")


def largest_rectangle(heights: list[int]) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [[2, 1, 5, 6, 2, 3], [2, 4], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [3, 3, 3],
             [0, 0], [6, 2, 5, 4, 5, 1, 6], []]
    for h in cases:
        ans = largest_rectangle(h)
        print(f"{h!s:<24} -> {ans:>2}  agree={ans == with_boundaries(h) == brute_force(h)}")


if __name__ == "__main__":
    main()
