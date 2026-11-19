"""
Exercise 10 — Top-K Largest: Heap, Then Quickselect                [Tier: ◆ Extended]
Chapter 15 · Pattern: size-k heap vs partition-based selection · Target time: 25 min

Problem
-------
Return the k largest values of a list in descending order (duplicates count separately).
Implement it three ways and say when each one wins. Do not modify the caller's list.

(§11.13 teaches the quickselect algorithm for the single k-th element; here it is the
"can you beat O(n log k)?" follow-up to a top-k heap answer.)

Examples
--------
>>> solve([3, 1, 4, 1, 5, 9, 2, 6], 3)
[9, 6, 5]
>>> solve([2, 2, 2, 1], 2)
[2, 2]

Constraints
-----------
- 0 <= k <= len(nums) <= 10^6; ints.

Hints
-----
- Target index in ascending order is n - k; everything right of it must be >= it.
- 3-way partition (< pivot | == pivot | > pivot) keeps all-equal input linear.
- Seed the RNG so runs are reproducible.

Follow-ups
----------
- Guaranteed O(n): median-of-medians pivots (name it, rarely coded).
- Data does not fit in memory or arrives as a stream: only the heap works.
- Need the k-th value only: stop after selection, skip the final sort (§11.13).

Wrong-but-tempting
------------------
- Two-way partition with `<=` on all-equal input: every split is n-1 / 0 -> O(n^2).
- Quickselect on the caller's list: reorders their data as a side effect.
"""
from __future__ import annotations

import heapq
import random


def by_sort(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def by_heap(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def by_quickselect(nums: list[int], k: int, seed: int = 0) -> list[int]:
    raise NotImplementedError("TODO")


def solve(nums: list[int], k: int) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [([3, 1, 4, 1, 5, 9, 2, 6], 3), ([2, 2, 2, 1], 2), ([5], 1),
             ([7, -1, 7, 3], 0), ([-3, -1, -2], 3)]
    for nums, k in cases:
        before = list(nums)
        ans = solve(nums, k)
        agree = ans == by_sort(nums, k) == by_heap(nums, k) == heapq.nlargest(k, nums)
        print(f"k={k} {nums} -> {ans}  agree={agree}  input unchanged={nums == before}")
    rng = random.Random(15)
    ok = True
    for _ in range(400):
        nums = [rng.randint(-4, 4) for _ in range(rng.randint(0, 30))]
        k = rng.randint(0, len(nums))
        ok &= solve(nums, k) == by_sort(nums, k) == by_heap(nums, k)
    print("400 random duplicate-heavy cases agree:", ok)
    same = [7] * 20000
    print("20000 equal values, k=10000 ->", solve(same, 10000)[:3], "... len",
          len(solve(same, 10000)))


if __name__ == "__main__":
    main()
