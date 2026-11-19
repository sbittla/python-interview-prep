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

Approach ladder
---------------
1. Brute force — ``max(nums[i:i+k])`` for every window. O(n*k) time, O(k) per slice.
2. Improved   — a max-heap of ``(-value, index)``; before reading the top, lazily pop
   entries whose index has left the window. O(n log n) time, O(n) space. Why not stop here:
   stale entries pile up, and the log factor is avoidable.
3. Optimal    — a deque of indices whose values are *decreasing* front to back. For each new
   index: pop from the back every index with value ``<=`` the new value (they can never be a
   window maximum again: the new value is at least as big and lives longer), append the new
   index, drop the front if it fell out of the window, and read ``nums[dq[0]]``. Each index
   enters and leaves the deque at most once: O(n) time, O(k) space.

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
    if nums and not 1 <= k <= len(nums):
        raise ValueError(f"window size must be in 1..{len(nums)}, got {k}")


def brute_force(nums: list[int], k: int) -> list[int]:
    _check(nums, k)
    return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)] if nums else []


def with_heap(nums: list[int], k: int) -> list[int]:
    _check(nums, k)
    heap: list[tuple[int, int]] = []
    out = []
    for i, x in enumerate(nums):
        heapq.heappush(heap, (-x, i))
        if i >= k - 1:
            while heap[0][1] <= i - k:         # lazy delete expired maxima
                heapq.heappop(heap)
            out.append(-heap[0][0])
    return out


def max_sliding_window(nums: list[int], k: int) -> list[int]:
    _check(nums, k)                            # ValueError unless 1 <= k <= len(nums)
    dq: deque[int] = deque()                   # indices; values decreasing front→back
    out = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()                           # dominated: can never be a max again
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()                       # front left the window
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out


def trace(nums: list[int], k: int) -> list[str]:
    """Same algorithm, logging the deque (as values) after each step."""
    lines = [f"{'i':>2} {'x':>3}  deque (values)   max"]
    dq: deque[int] = deque()
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        shown = str([nums[j] for j in dq])
        lines.append(f"{i:>2} {x:>3}  {shown:<16} {nums[dq[0]] if i >= k - 1 else '-'}")
    return lines


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
