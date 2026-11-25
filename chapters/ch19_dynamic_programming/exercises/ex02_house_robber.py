"""
Exercise 02 — House Robber: Line and Circle                         [Tier: ★ Core]
Chapter 19 · Pattern: 1D DP, take/skip · Target time: 25 min

Problem
-------
Houses stand in a row; nums[i] >= 0 is the cash in house i. Robbing two adjacent
houses trips the alarm.
1. `rob(nums)` — the most cash you can take from the row.
2. `rob_with_houses(nums)` — the same total plus the (sorted) indices of one optimal
   set of houses.
3. `rob_circular(nums)` — the houses stand in a circle, so the first and last are
   adjacent too.

Examples
--------
>>> rob([2, 7, 9, 3, 1])
12
>>> rob_with_houses([2, 7, 9, 3, 1])
(12, [0, 2, 4])
>>> rob_circular([2, 3, 2]), rob_circular([1, 2, 3, 1])
(3, 4)

Constraints
-----------
- 0 <= len(nums) <= 10^5, 0 <= nums[i] <= 10^4. Empty input returns 0 (and []).

Hints
-----
- The memoised rung recurses ~n deep and hits the ~1000 limit (section 7.21) well inside
  the constraints; this is why the final answer is a table.
- At house i you have exactly two choices; write the max of them.
- To reconstruct, walk the table backwards: if best(i) == best(i-1) house i-1 was
  skipped, otherwise it was taken and you jump to i-2.
- For the circle, break it: some optimal answer skips house 0 or skips house n-1.

Follow-ups
----------
- Houses on a binary tree (exercise 10, section 19.12).
- "Delete and earn": bucket equal values, then it is this problem on the value line.
"""
from __future__ import annotations

from functools import cache


def rob_brute(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def rob_memo(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def _table(nums: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def rob_table(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def rob(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def rob_with_houses(nums: list[int]) -> tuple[int, list[int]]:
    raise NotImplementedError("TODO")


def rob_circular_brute(nums: list[int]) -> int:
    """Try every subset of houses (O(2^n * n)); reject any with adjacent pairs."""
    raise NotImplementedError("TODO")


def rob_circular(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    for nums in ([2, 7, 9, 3, 1], [1, 2, 3, 1], [2, 1, 1, 2], [5], []):
        rungs = (rob_brute(nums), rob_memo(nums), rob_table(nums), rob(nums))
        print(f"rob({nums}) = {rob(nums):<3} with houses {rob_with_houses(nums)[1]}"
              f"  rungs agree: {len(set(rungs)) == 1}")
    for nums in ([2, 3, 2], [1, 2, 3, 1], [1, 2, 3], [200, 3, 140, 20, 10], [7]):
        print(f"rob_circular({nums}) = {rob_circular(nums)}  brute = {rob_circular_brute(nums)}")


if __name__ == "__main__":
    main()
