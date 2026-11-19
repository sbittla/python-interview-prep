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

Hints
-----
- Water at i = min(max to the left, max to the right) - height[i].
- Cache both maxima in arrays, then remove the arrays with two pointers.
- Which side's maximum decides the water level when left_max <= right_max?
- Stack version: fill water in horizontal layers when a taller wall arrives.

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
    raise NotImplementedError("TODO")


def prefix_max(heights: list[int]) -> int:
    raise NotImplementedError("TODO")


def trap(heights: list[int]) -> int:           # two pointers, O(1) extra space
    raise NotImplementedError("TODO")


def trap_stack(heights: list[int]) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], [4, 2, 0, 3, 2, 5], [1, 2, 3], [3, 0, 3],
             [5, 0, 0, 0, 1], [], [2]]
    for h in cases:
        answers = [brute_force(h), prefix_max(h), trap(h), trap_stack(h)]
        print(f"{h!s:<38} -> {answers[2]:>2}  agree={len(set(answers)) == 1}")


if __name__ == "__main__":
    main()
