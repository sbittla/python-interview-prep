"""
Exercise 10 — Count Subarrays Summing to k               [Tier: ★ Core]
Chapter 10 · Pattern: prefix sum + hash map · Target time: 20 min

Problem
-------
Given integers nums (negatives and zeros allowed) and an integer k, return the
number of non-empty contiguous subarrays whose sum is exactly k.
longest(nums, k) returns the length of the longest such subarray (0 if none).

Examples
--------
>>> solve([1, 1, 1], 2)
2
>>> solve([3, 4, -7, 3, 1, 3, 1, -4], 7)   # [3,4], [3,4,-7,3,1,3], [3,1,3]
3
>>> longest([1, -1, 5, -2, 3], 3)
4

Constraints
-----------
- 0 <= len(nums) <= 2 * 10**4; -1000 <= nums[i] <= 1000.

Hints
-----
- sum(nums[i:j]) == P[j] - P[i] where P is the prefix-sum array.
- Count earlier prefixes equal to P[j] - k with a Counter seeded {0: 1}.
- Why does a sliding window fail here? Try [1, -1, 1, -1] with k = 0.

Wrong-but-tempting
------------------
- A sliding window (grow right, shrink left while sum > k). It relies on
  "adding an element never decreases the sum", which fails once negatives
  appear (and zeros make it under-count). Correct only for strictly
  positive nums. With negatives, prefix sums are the tool.
- Forgetting the {0: 1} seed: misses every subarray that starts at index 0.
- Recording P[j] before the lookup: with k == 0 it counts empty subarrays.

Follow-ups
----------
- Count subarrays with sum divisible by m: key = P mod m.
- Longest subarray with equal 0s and 1s: map 0 -> -1, then longest sum 0.
- 2D version (count submatrices summing to k): fix a row pair, compress
  columns, run this 1D routine. O(r^2 * c).
"""
from __future__ import annotations

from collections import Counter


def brute_force(nums: list[int], k: int) -> int:
    raise NotImplementedError("TODO")


def running_sum(nums: list[int], k: int) -> int:
    raise NotImplementedError("TODO")


def wrong_sliding_window(nums: list[int], k: int) -> int:
    """Wrong-but-tempting: correct only when every element is positive."""
    count = left = window = 0
    for right, x in enumerate(nums):
        window += x
        while window > k and left <= right:
            window -= nums[left]
            left += 1
        if window == k and left <= right:
            count += 1
    return count


def solve(nums: list[int], k: int) -> int:
    raise NotImplementedError("TODO")


def longest_brute(nums: list[int], k: int) -> int:
    raise NotImplementedError("TODO")


def longest(nums: list[int], k: int) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [([1, 1, 1], 2), ([1, 2, 3], 3), ([3, 4, -7, 3, 1, 3, 1, -4], 7), ([1, -1, 1, -1], 0),
             ([0, 0, 0], 0), ([], 5), ([2, 1, 3, 2, 1], 3)]
    for nums, k in cases:
        print(f"nums={nums!s:<28} k={k} -> {solve(nums, k):<2} brute={brute_force(nums, k):<2}"
              f" longest={longest(nums, k)}  sliding-window(wrong)={wrong_sliding_window(nums, k)}")


if __name__ == "__main__":
    main()
