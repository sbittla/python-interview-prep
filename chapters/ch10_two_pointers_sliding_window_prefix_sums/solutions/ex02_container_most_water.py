"""
Exercise 02 — Container With Most Water                  [Tier: ★ Core]
Chapter 10 · Pattern: opposite-direction two pointers (greedy discard) · Target time: 15 min

Problem
-------
heights[i] >= 0 is the height of a vertical wall at x = i. Choose two walls
i < j; together with the x-axis they hold (j - i) * min(heights[i], heights[j])
units of water. Return the largest amount any pair can hold (0 if there are
fewer than two walls).

Examples
--------
>>> solve([1, 8, 6, 2, 5, 4, 8, 3, 7])
49
>>> solve([1, 1])
1

Constraints
-----------
- 0 <= len(heights) <= 10**5; 0 <= heights[i] <= 10**4.

Approach ladder
---------------
1. Brute force — try every pair. O(n^2) time, O(1) space. Too slow at 10**5.
2. Optimal    — start with the widest pair (0, n-1). Its area is capped by the
   shorter wall. Every other pair that keeps the shorter wall is narrower and
   still capped by that wall, so it can never beat the current pair: the
   shorter wall is *finished* and we move it inward. O(n) time, O(1) space.
   (There is no useful middle rung: sorting destroys the positions.)

Invariant: every pair not yet examined lies inside [lo, hi], and the best
pair outside it has already been recorded.

Wrong-but-tempting
------------------
- Moving the taller wall: it discards pairs that may be optimal.

Follow-ups
----------
- Equal heights: moving either pointer is safe (neither wall can do better
  with any wall inside).
- Trapping rain water (total over all bars) is a different problem: two
  pointers with running maxima, or a monotonic stack (-> Chapter 12.5).
"""
from __future__ import annotations


def brute_force(heights: list[int]) -> int:
    best = 0
    for i in range(len(heights)):
        for j in range(i + 1, len(heights)):
            best = max(best, (j - i) * min(heights[i], heights[j]))
    return best


def wrong_move_taller(heights: list[int]) -> int:
    """Wrong-but-tempting: moves the taller wall instead of the shorter one."""
    lo, hi, best = 0, len(heights) - 1, 0
    while lo < hi:
        best = max(best, (hi - lo) * min(heights[lo], heights[hi]))
        if heights[lo] > heights[hi]:
            lo += 1
        else:
            hi -= 1
    return best


def solve(heights: list[int]) -> int:
    lo, hi, best = 0, len(heights) - 1, 0
    while lo < hi:
        best = max(best, (hi - lo) * min(heights[lo], heights[hi]))
        if heights[lo] < heights[hi]:
            lo += 1                       # short wall is finished
        else:
            hi -= 1
    return best


def main() -> None:
    cases = [[1, 8, 6, 2, 5, 4, 8, 3, 7], [1, 1], [4, 3, 2, 1, 4], [1, 2, 1], [5], [],
             [2, 9, 9, 1, 1, 1]]
    for h in cases:
        print(f"heights={h!s:<28} -> {solve(h):<3} brute={brute_force(h):<3}"
              f" move-taller(wrong)={wrong_move_taller(h)}")


if __name__ == "__main__":
    main()
