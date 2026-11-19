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

Approach ladder
---------------
1. Brute force — for each i scan right (or around the circle) until a bigger value appears.
   O(n^2) time on a decreasing list, O(1) extra.
2. Optimal    — scan left to right keeping a stack of indices whose answer is still unknown.
   Their values are non-increasing from bottom to top (a monotonic stack). When ``x``
   arrives, it is the answer for every stacked index with a smaller value: pop them all, then
   push ``i``. Each index is pushed once and popped at most once, so O(n) total, O(n) space.
   Circular: run the scan over ``2n`` positions using ``i % n`` and only push during the first
   lap. Why move up: the brute force rescans the same elements; the stack remembers exactly
   the candidates still waiting.

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
    out: list[int | None] = []
    for i, x in enumerate(nums):
        out.append(next((y for y in nums[i + 1:] if y > x), None))
    return out


def brute_force_circular(nums: list[int]) -> list[int | None]:
    n = len(nums)
    out: list[int | None] = []
    for i, x in enumerate(nums):
        out.append(next((nums[(i + d) % n] for d in range(1, n) if nums[(i + d) % n] > x), None))
    return out


def brute_force_smaller(nums: list[int]) -> list[int | None]:
    return [next((y for y in nums[i + 1:] if y < x), None) for i, x in enumerate(nums)]


def next_greater(nums: list[int]) -> list[int | None]:
    out: list[int | None] = [None] * len(nums)
    stack: list[int] = []                      # indices; values non-increasing
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            out[stack.pop()] = x               # x is the first bigger value
        stack.append(i)
    return out


def next_greater_circular(nums: list[int]) -> list[int | None]:
    n = len(nums)
    out: list[int | None] = [None] * n
    stack: list[int] = []
    for k in range(2 * n):
        x = nums[k % n]
        while stack and nums[stack[-1]] < x:
            out[stack.pop()] = x
        if k < n:                              # push each index only on the first lap
            stack.append(k)
    return out


def next_smaller(nums: list[int]) -> list[int | None]:
    out: list[int | None] = [None] * len(nums)
    stack: list[int] = []                      # values non-decreasing
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] > x:
            out[stack.pop()] = x
        stack.append(i)
    return out


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
