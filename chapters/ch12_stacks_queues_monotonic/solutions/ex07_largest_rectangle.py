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

Approach ladder
---------------
1. Brute force — for every left edge ``i`` extend right, tracking the running minimum
   height; area = ``min_h * width``. O(n^2) time, O(1) space.
2. Improved   — the best rectangle that uses bar ``i`` as its *shortest* bar spans from the
   previous smaller bar to the next smaller bar. Compute both boundaries with two
   monotonic-stack passes (exercise 04's template), then take
   ``max(h[i] * (right[i] - left[i] - 1))``. O(n) time, O(n) space, three passes.
3. Optimal    — one pass with a non-decreasing stack of indices. When bar ``i`` is lower than
   the top, the top's right boundary is ``i`` and its left boundary is the index *below* it
   on the stack, so its area can be computed at pop time. A sentinel height 0 at the end
   flushes the stack. O(n) time (each index pushed/popped once), O(n) space.
   Why move up: rung 2 shows *why* it works; rung 3 is the compact version interviewers
   expect once you have explained rung 2.

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
    best = 0
    for i in range(len(heights)):
        min_h = heights[i]
        for j in range(i, len(heights)):
            min_h = min(min_h, heights[j])
            best = max(best, min_h * (j - i + 1))
    return best


def with_boundaries(heights: list[int]) -> int:
    n = len(heights)
    left, right = [-1] * n, [n] * n            # previous / next strictly smaller index
    stack: list[int] = []
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] >= h:
            stack.pop()
        left[i] = stack[-1] if stack else -1
        stack.append(i)
    stack.clear()
    for i in range(n - 1, -1, -1):
        while stack and heights[stack[-1]] >= heights[i]:
            stack.pop()
        right[i] = stack[-1] if stack else n
        stack.append(i)
    return max((heights[i] * (right[i] - left[i] - 1) for i in range(n)), default=0)


def largest_rectangle(heights: list[int]) -> int:
    best = 0
    stack: list[int] = []                      # indices; heights non-decreasing
    for i, h in enumerate(heights + [0]):      # sentinel 0 flushes the stack
        while stack and heights[stack[-1]] > h:
            top = stack.pop()
            left = stack[-1] if stack else -1  # previous smaller bar
            best = max(best, heights[top] * (i - left - 1))
        stack.append(i)
    return best


def main() -> None:
    cases = [[2, 1, 5, 6, 2, 3], [2, 4], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [3, 3, 3],
             [0, 0], [6, 2, 5, 4, 5, 1, 6], []]
    for h in cases:
        ans = largest_rectangle(h)
        print(f"{h!s:<24} -> {ans:>2}  agree={ans == with_boundaries(h) == brute_force(h)}")


if __name__ == "__main__":
    main()
