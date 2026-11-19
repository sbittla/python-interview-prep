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

Hints
-----
- Start with the widest pair; the area is capped by the shorter wall.
- Which wall can never be part of a better pair with anything inside? Move that one.

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
    raise NotImplementedError("TODO")


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
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [[1, 8, 6, 2, 5, 4, 8, 3, 7], [1, 1], [4, 3, 2, 1, 4], [1, 2, 1], [5], [],
             [2, 9, 9, 1, 1, 1]]
    for h in cases:
        print(f"heights={h!s:<28} -> {solve(h):<3} brute={brute_force(h):<3}"
              f" move-taller(wrong)={wrong_move_taller(h)}")


if __name__ == "__main__":
    main()
