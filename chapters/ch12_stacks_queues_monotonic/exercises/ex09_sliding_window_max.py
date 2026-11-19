"""
Exercise 09 — Sliding Window Maximum                          [Tier: ★ Core]
Chapter 12 · Pattern: monotonic deque (canonical home, §12.6) · Target time: 25 min

Problem
-------
Given a list ``nums`` and a window size ``k``, return the maximum of every contiguous window of
length ``k``, from left to right (``len(nums) - k + 1`` values). Raise ``ValueError`` unless
``1 <= k <= len(nums)``; an empty ``nums`` returns ``[]``.

Examples
--------
>>> max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)
[3, 3, 5, 5, 6, 7]

Constraints
-----------
- 0 <= len(nums) <= 10**5; values may repeat and be negative.

Hints
-----
- A heap works if you lazily discard entries that have left the window.
- Deque of indices with decreasing values: pop smaller-or-equal values from the back and expired indices from the front; the front is then the window max.

Wrong-but-tempting
------------------
- Keeping only one running max: when the max leaves the window you must rescan.
- Storing values instead of indices in the deque: you cannot tell when the front expired.
- Using a ``list`` and ``pop(0)``: O(k) per front pop; use ``collections.deque``.
- Reading the answer before the first window is full (``i >= k - 1`` guard).

Follow-ups
----------
- Sliding window minimum: flip the comparison.
- Longest subarray where ``max - min <= limit``: two deques plus a variable window (→ §10.5).
- Shortest subarray with sum at least K (negatives allowed): monotonic deque over prefix sums.
"""
from __future__ import annotations

import heapq
from collections import deque


def _check(nums: list[int], k: int) -> None:
    raise NotImplementedError("TODO")


def brute_force(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def with_heap(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def max_sliding_window(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def trace(nums: list[int], k: int) -> list[str]:
    """Same algorithm, logging the deque (as values) after each step."""
    raise NotImplementedError("TODO")


def main() -> None:
    nums, k = [1, 3, -1, -3, 5, 3, 6, 7], 3
    print("\n".join(trace(nums, k)))
    cases = [(nums, k), ([4, 4, 4, 1], 2), ([9, 8, 7, 6], 2), ([1, 2, 3], 1), ([5, -1], 2), ([], 3)]
    for arr, w in cases:
        ans = max_sliding_window(arr, w)
        ok = ans == with_heap(arr, w) == brute_force(arr, w)
        print(f"k={w} {arr!s:<28} -> {ans}  agree={ok}")
    try:
        max_sliding_window([1, 2], 3)
    except ValueError as e:
        print(f"k too large -> ValueError: {e}")


if __name__ == "__main__":
    main()
