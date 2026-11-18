"""
Exercise 13 — Quickselect: K-th Largest Element                    [Tier: ◆ Extended]
Chapter 11 · Pattern: partition and recurse into ONE side · Target time: 20 min

Problem
-------
Return the k-th largest element of an unsorted list (k = 1 is the maximum).
Duplicates count separately: in [3, 3, 2] the 2nd largest is 3.

Examples
--------
>>> solve([3, 2, 1, 5, 6, 4], 2)
5
>>> solve([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)
4

Constraints
-----------
- 1 <= k <= len(nums) <= 10^5.

Approach ladder
---------------
1. Brute force — sort descending, index k-1: O(n log n).
2. Improved   — min-heap of size k: keep the k largest seen; the root is the
   answer. O(n log k) time, O(k) space. Works on a stream.
3. Optimal    — quickselect: partition around a random pivot; the pivot's
   final index tells you which ONE side holds the answer. Expected
   n + n/2 + n/4 + ... = O(n), worst case O(n^2) (made unlikely by randomness).
   Use a three-way partition so heavy duplicates do not degrade it.

Follow-ups
----------
- Guaranteed O(n): median-of-medians pivot (rarely coded in interviews; name it).
- k closest points to the origin: quickselect on distance.
- Median of an unsorted list: quickselect for n // 2.
- Streaming: the heap approach; quickselect needs all the data.
"""
from __future__ import annotations

import heapq
import random


def brute_force(nums: list[int], k: int) -> int:
    return sorted(nums, reverse=True)[k - 1]


def heap_select(nums: list[int], k: int) -> int:
    heap: list[int] = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)       # pop smallest, push x
    return heap[0]


def solve(nums: list[int], k: int, seed: int = 0) -> int:
    """Iterative quickselect with a 3-way partition. Target index in ascending order is n - k."""
    a = list(nums)
    rng = random.Random(seed)
    target = len(a) - k
    lo, hi = 0, len(a) - 1
    while True:
        pivot = a[rng.randint(lo, hi)]
        lt, i, gt = lo, lo, hi
        while i <= gt:                       # Dutch national flag partition of a[lo..hi]
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
            hi = lt - 1                      # answer is in the "< pivot" block
        elif target > gt:
            lo = gt + 1                      # answer is in the "> pivot" block
        else:
            return pivot                     # target falls inside the "== pivot" block


def kth_smallest(nums: list[int], k: int) -> int:
    return solve(nums, len(nums) - k + 1)


def k_closest(points: list[tuple[int, int]], k: int) -> list[tuple[int, int]]:
    """k points closest to the origin, returned sorted for deterministic output."""
    if k >= len(points):
        return sorted(points)
    dists = [x * x + y * y for x, y in points]
    cutoff = kth_smallest(dists, k)          # k-th smallest squared distance
    closer = [p for p, d in zip(points, dists) if d < cutoff]
    ties = [p for p, d in zip(points, dists) if d == cutoff]
    return sorted(closer + ties[: k - len(closer)])


def main() -> None:
    nums = [3, 2, 1, 5, 6, 4]
    for k in range(1, len(nums) + 1):
        print(f"k={k}: quickselect={solve(nums, k)} heap={heap_select(nums, k)} "
              f"sort={brute_force(nums, k)}")
    dup = [3, 2, 3, 1, 2, 4, 5, 5, 6]
    print("duplicates, k=4:", solve(dup, 4), heap_select(dup, 4), brute_force(dup, 4))
    print("all equal, k=3:", solve([7] * 10, 3))
    print("single element:", solve([42], 1))
    print("median of [9, 1, 8, 2, 7, 3, 6]:", kth_smallest([9, 1, 8, 2, 7, 3, 6], 4))
    rng = random.Random(7)
    big = [rng.randint(-1000, 1000) for _ in range(2000)]
    print("random 2000 values, all k in steps of 250 agree:",
          all(solve(big, k) == brute_force(big, k) for k in range(1, 2001, 250)))
    print("2 closest points:", k_closest([(1, 3), (-2, 2), (5, 8), (0, 1)], 2))


if __name__ == "__main__":
    main()
