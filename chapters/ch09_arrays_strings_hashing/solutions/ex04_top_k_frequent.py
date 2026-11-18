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

Approach ladder
---------------
1. Brute force — for each distinct value, nums.count(value). O(n * d) time.
2. Improved   — Counter + sort by (-count, value): O(n + d log d).
   heapq.nsmallest(k, ...) gives O(n + d log k) — best when k is small.
3. Optimal    — bucket sort by frequency: bucket[f] holds values seen f times;
   walk buckets from high f to low. O(n) time (plus sorting inside the few
   buckets we touch, for the deterministic tie-break).

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
    distinct = sorted(set(nums))
    scored = [(-nums.count(v), v) for v in distinct]     # O(n) per value
    scored.sort()
    return [v for _, v in scored[:k]]


def by_sort(nums: list[int], k: int) -> list[int]:
    counts = Counter(nums)
    return sorted(counts, key=lambda v: (-counts[v], v))[:k]


def by_heap(nums: list[int], k: int) -> list[int]:
    counts = Counter(nums)
    return [v for _, v in heapq.nsmallest(k, ((-c, v) for v, c in counts.items()))]


def solve(nums: list[int], k: int) -> list[int]:
    counts = Counter(nums)
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]
    for value, freq in counts.items():
        buckets[freq].append(value)
    out: list[int] = []
    for freq in range(len(buckets) - 1, 0, -1):
        for value in sorted(buckets[freq]):          # deterministic tie-break
            out.append(value)
            if len(out) == k:
                return out
    return out


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
