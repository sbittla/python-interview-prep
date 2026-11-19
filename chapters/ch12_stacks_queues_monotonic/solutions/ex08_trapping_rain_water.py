"""
Exercise 08 — Trapping Rain Water                             [Tier: ★ Core]
Chapter 12 · Pattern: prefix max → two pointers / monotonic stack · Target time: 30 min

Problem
-------
``heights[i]`` is the height of a wall of width 1. After rain, how many unit cells of water are
held between the walls? Water above position ``i`` rises to ``min(max left of i, max right of
i)`` and the wall itself takes up ``heights[i]`` of that.

Examples
--------
>>> trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])
6
>>> trap([4, 2, 0, 3, 2, 5])
9

Constraints
-----------
- 0 <= len(heights) <= 10**5; 0 <= heights[i] <= 10**5.

Approach ladder
---------------
1. Brute force — for each ``i`` scan both sides for the tallest wall (index loops, no
   slices). O(n^2) time, O(1) extra space.
2. Improved   — precompute ``left_max[i]`` and ``right_max[i]`` with two prefix passes, then
   sum ``min(left_max, right_max) - h``. O(n) time, O(n) space.
3. Optimal A (two pointers) — move inward from both ends keeping ``left_max`` and
   ``right_max``. If ``left_max <= right_max``, the water at ``lo`` is fully decided by
   ``left_max`` (the true right maximum is at least ``right_max``), so settle ``lo`` and step
   it. Symmetric for ``hi``. O(n) time, O(1) space.
   Optimal B (monotonic stack) — fills water *horizontally* in layers: keep a decreasing
   stack; when a taller wall arrives, pop the "floor" and add
   ``(min(left wall, right wall) - floor) * width``. O(n) time, O(n) space. Same complexity
   as rung 2 but shows the stack pattern; it generalises to "fill between walls" problems.
   Why move up: rung 1 recomputes the same maxima n times; rung 2 caches them; rung 3A
   notices that only the smaller side's maximum matters at each step.

Wrong-but-tempting
------------------
- Using ``max(left_max, right_max)``: water spills over the lower wall.
- Two pointers that move the side with the *taller* current wall: the water level at the
  other side is then undecided.
- Counting negative water when ``h`` exceeds the level (the formula is safe only because
  ``left_max`` includes ``h`` itself).

Follow-ups
----------
- 2-D version (Trapping Rain Water II): a min-heap flood fill from the border, O(mn log mn).
- Container With Most Water looks similar but is a different two-pointer problem (→ §10.1).
"""
from __future__ import annotations


def brute_force(heights: list[int]) -> int:
    total = 0
    n = len(heights)
    for i, h in enumerate(heights):
        left = right = h
        for j in range(i):
            left = max(left, heights[j])
        for j in range(i + 1, n):
            right = max(right, heights[j])
        total += min(left, right) - h
    return total


def prefix_max(heights: list[int]) -> int:
    n = len(heights)
    if n == 0:
        return 0
    left, right = [0] * n, [0] * n
    left[0], right[-1] = heights[0], heights[-1]
    for i in range(1, n):
        left[i] = max(left[i - 1], heights[i])
    for i in range(n - 2, -1, -1):
        right[i] = max(right[i + 1], heights[i])
    return sum(min(left[i], right[i]) - heights[i] for i in range(n))


def trap(heights: list[int]) -> int:           # two pointers, O(1) extra space
    lo, hi = 0, len(heights) - 1
    left_max = right_max = total = 0
    while lo <= hi:
        if left_max <= right_max:              # left side is the bottleneck
            left_max = max(left_max, heights[lo])
            total += left_max - heights[lo]
            lo += 1
        else:
            right_max = max(right_max, heights[hi])
            total += right_max - heights[hi]
            hi -= 1
    return total


def trap_stack(heights: list[int]) -> int:
    total = 0
    stack: list[int] = []                      # indices; heights decreasing
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] < h:
            floor = heights[stack.pop()]
            if not stack:
                break                          # no left wall: water runs off
            left = stack[-1]
            level = min(heights[left], h)
            total += (level - floor) * (i - left - 1)
        stack.append(i)
    return total


def main() -> None:
    cases = [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], [4, 2, 0, 3, 2, 5], [1, 2, 3], [3, 0, 3],
             [5, 0, 0, 0, 1], [], [2]]
    for h in cases:
        answers = [brute_force(h), prefix_max(h), trap(h), trap_stack(h)]
        print(f"{h!s:<38} -> {answers[2]:>2}  agree={len(set(answers)) == 1}")


if __name__ == "__main__":
    main()
