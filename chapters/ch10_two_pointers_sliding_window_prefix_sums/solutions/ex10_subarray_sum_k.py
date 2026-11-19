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

Approach ladder
---------------
1. Brute force — sum(nums[i:j]) for every pair. O(n^3) time.
2. Improved   — fix i, extend j with a running sum. O(n^2) time, O(1) space.
3. Optimal    — let P[j] = sum(nums[:j]). sum(nums[i:j]) == k  <=>
   P[i] == P[j] - k. Scan once, keeping a Counter of prefix sums seen so far
   (seeded with {0: 1} for the empty prefix); at each j add
   seen[P[j] - k] to the answer, THEN record P[j]. O(n) time, O(n) space.
   For the longest variant store the FIRST index of each prefix sum.

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
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i + 1, n + 1) if sum(nums[i:j]) == k)


def running_sum(nums: list[int], k: int) -> int:
    count = 0
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            count += total == k
    return count


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
    seen = Counter({0: 1})                # prefix sum of the empty prefix
    prefix = count = 0
    for x in nums:
        prefix += x
        count += seen[prefix - k]         # earlier prefixes P[i] = P[j] - k
        seen[prefix] += 1                 # record AFTER the lookup
    return count


def longest_brute(nums: list[int], k: int) -> int:
    n = len(nums)
    return max((j - i for i in range(n) for j in range(i + 1, n + 1)
                if sum(nums[i:j]) == k), default=0)


def longest(nums: list[int], k: int) -> int:
    first = {0: 0}                        # prefix sum -> earliest index
    prefix = best = 0
    for j, x in enumerate(nums, start=1):
        prefix += x
        if prefix - k in first:
            best = max(best, j - first[prefix - k])
        first.setdefault(prefix, j)
    return best


def main() -> None:
    cases = [([1, 1, 1], 2), ([1, 2, 3], 3), ([3, 4, -7, 3, 1, 3, 1, -4], 7), ([1, -1, 1, -1], 0),
             ([0, 0, 0], 0), ([], 5), ([2, 1, 3, 2, 1], 3)]
    for nums, k in cases:
        print(f"nums={nums!s:<28} k={k} -> {solve(nums, k):<2} brute={brute_force(nums, k):<2}"
              f" longest={longest(nums, k)}  sliding-window(wrong)={wrong_sliding_window(nums, k)}")


if __name__ == "__main__":
    main()
