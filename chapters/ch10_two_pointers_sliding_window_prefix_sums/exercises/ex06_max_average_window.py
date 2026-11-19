"""
Exercise 06 — Best Fixed-Size Window (sum, average, maxima)  [Tier: ★ Core]
Chapter 10 · Pattern: fixed-size sliding window; bridge to monotonic deque · Target time: 15 min

Problem
-------
(a) solve(nums, k): return the largest sum of any k consecutive elements
    (the best average is that sum / k, so we keep integers and avoid floats).
(b) window_maxima(nums, k): return the maximum of every window of size k,
    left to right (n - k + 1 values).

Examples
--------
>>> solve([1, 12, -5, -6, 50, 3], 4)       # window [12, -5, -6, 50]
51
>>> max_average([1, 12, -5, -6, 50, 3], 4)
12.75
>>> window_maxima([1, 3, -1, -3, 5, 3, 6, 7], 3)
[3, 3, 5, 5, 6, 7]

Constraints
-----------
- 1 <= k <= len(nums) <= 10**5; values may be negative. solve raises ValueError
  otherwise (k > len(nums) would silently return the whole-array sum).

Hints
-----
- Fixed window: add the element entering, subtract the one leaving.
- Initialise best with the first window, not 0.
- Window maxima: a max cannot be 'subtracted'; keep a deque of decreasing values.

Wrong-but-tempting
------------------
- Initialising best = 0: wrong when every window sum is negative.
- Off-by-one in the loop bound: range(k, len(nums)) is correct for the
  entering index; range(k, len(nums) - 1) misses the last window.

Follow-ups
----------
- Count windows whose average >= threshold: compare sum >= threshold * k.
- Window minimum / median: deque of increasing values / two heaps.
"""
from __future__ import annotations

from collections import deque
from itertools import accumulate


def brute_force(nums: list[int], k: int) -> int:
    raise NotImplementedError("TODO")


def prefix_sums(nums: list[int], k: int) -> int:
    raise NotImplementedError("TODO")


def wrong_zero_init(nums: list[int], k: int) -> int:
    """Wrong-but-tempting: best starts at 0 instead of the first window."""
    window = best = 0
    for i, x in enumerate(nums):
        window += x
        if i >= k:
            window -= nums[i - k]
        if i >= k - 1:
            best = max(best, window)
    return best


def wrong_off_by_one(nums: list[int], k: int) -> int:
    """Wrong-but-tempting: the loop bound stops one window early."""
    window = best = sum(nums[:k])
    for i in range(k, len(nums) - 1):     # bug: never adds the last element
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best


def solve(nums: list[int], k: int) -> int:
    raise NotImplementedError("TODO")


def max_average(nums: list[int], k: int) -> float:
    raise NotImplementedError("TODO")


def window_maxima_brute(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def window_maxima(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [([1, 12, -5, -6, 50, 3], 4), ([5], 1), ([-3, -1, -2], 2), ([4, 0, 4, 3, 3], 5),
             ([1, 3, -1, -3, 5, 3, 6, 7], 3)]
    for nums, k in cases:
        print(f"nums={nums!s:<27} k={k} -> max sum {solve(nums, k):<3}"
              f" avg {max_average(nums, k):<6.2f} brute={brute_force(nums, k):<3}"
              f" zero-init(wrong)={wrong_zero_init(nums, k)}")
        print(f"{'':35}window maxima {window_maxima(nums, k)}"
              f"  brute agrees: {window_maxima_brute(nums, k) == window_maxima(nums, k)}")


if __name__ == "__main__":
    main()
