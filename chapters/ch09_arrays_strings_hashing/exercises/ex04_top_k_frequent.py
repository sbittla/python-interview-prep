"""
Exercise 04 — Top K Frequent Elements                    [Tier: ★ Core]
Chapter 09 · Pattern: frequency counting + bucket sort · Target time: 15 min

Problem
-------
Given a list of integers and k, return the k values that occur most often.
Break ties by smaller value first so the answer is deterministic, and return the
answer ordered by (frequency descending, value ascending).

Examples
--------
>>> solve([1, 1, 1, 2, 2, 3], 2)
[1, 2]
>>> solve([4, 4, 5, 5, 6], 2)
[4, 5]

Constraints
-----------
- 1 <= k <= number of distinct values
- len(nums) <= 10**5

Hints
-----
- Count with Counter first.
- Bucket sort: a list indexed by frequency (0..n) of value lists; walk from high to low.
- Sort values inside a bucket for the deterministic tie-break (smaller value first).

Follow-ups
----------
- Streaming data: keep a Counter plus a size-k min-heap (Chapter 15).
- Top-k frequent words with lexicographic tie-break: same key (-count, word).
- Very large d with small k: heap beats full sort.
"""
from __future__ import annotations

import heapq
from collections import Counter


def brute_force(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def by_sort(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def by_heap(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def solve(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [([1, 1, 1, 2, 2, 3], 2), ([4, 4, 5, 5, 6], 2), ([7], 1),
             ([3, 1, 2, 3, 1, 3, -1, -1, -1], 3)]
    for nums, k in cases:
        ans = solve(nums, k)
        agree = ans == brute_force(nums, k) == by_sort(nums, k) == by_heap(nums, k)
        print(f"k={k} nums={nums} -> {ans}  agree={agree}")
    print("Counter.most_common(2):", Counter("mississippi").most_common(2))


if __name__ == "__main__":
    main()
