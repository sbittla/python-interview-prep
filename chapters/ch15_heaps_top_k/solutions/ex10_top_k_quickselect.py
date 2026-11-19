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

Approach ladder
---------------
1. Sort        — `sorted(nums, reverse=True)[:k]`: O(n log n) time, O(n) space.
2. Size-k heap — min-heap of the k largest seen (what `heapq.nlargest` does):
   O(n log k) time, O(k) extra space; streams; the default answer.
3. Quickselect — copy, then partition (3-way, random pivot) until index n - k is in
   final position; then a[n-k:] holds the k largest (unordered). Sort only those:
   O(n + k log k) expected time, O(n) for the copy; O(n^2) worst case with bad pivots.
   Why move up: when k is close to n, log k ~ log n and the heap buys nothing.

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
    return sorted(nums, reverse=True)[:k]


def by_heap(nums: list[int], k: int) -> list[int]:
    if k <= 0:
        return []
    heap: list[int] = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    return sorted(heap, reverse=True)


def by_quickselect(nums: list[int], k: int, seed: int = 0) -> list[int]:
    if k <= 0:
        return []
    a, rng = list(nums), random.Random(seed)
    target = len(a) - k                                # final ascending index of k-th largest
    lo, hi = 0, len(a) - 1
    while lo < hi:
        pivot = a[rng.randint(lo, hi)]
        lt, i, gt = lo, lo, hi                          # a[lo:lt] < p, a[lt:i] == p, a[gt+1:hi+1] > p
        while i <= gt:
            if a[i] < pivot:
                a[lt], a[i] = a[i], a[lt]
                lt += 1
                i += 1
            elif a[i] > pivot:
                a[i], a[gt] = a[gt], a[i]
                gt -= 1
            else:
                i += 1
        if target < lt:
            hi = lt - 1
        elif target > gt:
            lo = gt + 1
        else:
            break                                      # target lands in the == block
    return sorted(a[target:], reverse=True)


def solve(nums: list[int], k: int) -> list[int]:
    return by_quickselect(nums, k)


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
