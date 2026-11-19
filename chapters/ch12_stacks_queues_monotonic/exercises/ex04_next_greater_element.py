"""
Exercise 04 — Next Greater / Smaller Element (Linear and Circular)   [Tier: ★ Core]
Chapter 12 · Pattern: monotonic stack · Target time: 20 min

Problem
-------
For each position ``i`` of a list of integers, find the first value to its right that is
strictly greater than ``nums[i]``; use ``None`` when there is none.

- ``next_greater(nums)``           — the list ends at the last element.
- ``next_greater_circular(nums)``  — the search wraps around to the start (each element is
  still compared with at most ``n - 1`` others, so an element never "finds itself").
- ``next_smaller(nums)``           — first value to the right that is strictly smaller.

Examples
--------
>>> next_greater([2, 1, 2, 4, 3])
[4, 2, 4, None, None]
>>> next_greater_circular([2, 1, 2, 4, 3])
[4, 2, 4, None, 4]
>>> next_smaller([4, 1, 3, 2])
[1, None, 2, None]

Constraints
-----------
- 0 <= len(nums) <= 10**5; values may repeat and may be negative.

Hints
-----
- Keep a stack of indices whose answer is still unknown; what order are their values in?
- The new value answers every stacked index with a smaller value.
- Circular: walk 2n positions with i % n, pushing only on the first lap.

Wrong-but-tempting
------------------
- Storing values instead of indices: you cannot write the answer back to the right slot.
- Popping on ``<=`` instead of ``<``: equal values would be reported as "greater".
- Circular version with one lap only: the tail never sees the start of the list. Copying
  ``nums + nums`` works but costs O(n) extra memory; ``i % n`` avoids the copy.
- Thinking the nested ``while`` makes it O(n^2) (see the amortised argument in the chapter).

Follow-ups
----------
- Return distances instead of values (exercise 06, daily temperatures).
- Previous greater element: scan right to left, or read the stack top *before* pushing.
- Next greater element for a subset query list: precompute with a dict from value to answer.
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> list[int | None]:
    raise NotImplementedError("TODO")


def brute_force_circular(nums: list[int]) -> list[int | None]:
    raise NotImplementedError("TODO")


def brute_force_smaller(nums: list[int]) -> list[int | None]:
    raise NotImplementedError("TODO")


def next_greater(nums: list[int]) -> list[int | None]:
    raise NotImplementedError("TODO")


def next_greater_circular(nums: list[int]) -> list[int | None]:
    raise NotImplementedError("TODO")


def next_smaller(nums: list[int]) -> list[int | None]:
    raise NotImplementedError("TODO")


def main() -> None:
    for nums in ([2, 1, 2, 4, 3], [5, 4, 3, 2, 1], [1, 1, 1], [3, 8, -2, 7, 9, 0], []):
        g, c, s = next_greater(nums), next_greater_circular(nums), next_smaller(nums)
        ok = (g == brute_force(nums) and c == brute_force_circular(nums)
              and s == brute_force_smaller(nums))
        print(f"nums     {nums}")
        print(f"greater  {g}")
        print(f"circular {c}")
        print(f"smaller  {s}   agree={ok}")


if __name__ == "__main__":
    main()
