"""
Exercise 09 — Counting Sort and Bucket Sort                        [Tier: ◆ Extended]
Chapter 11 · Pattern: non-comparison sorting / bucketing by key · Target time: 20 min

Problem
-------
(a) Sort integers whose range (max - min) is small, in O(n + k) time, where
k = max - min + 1. Negative values must work.
(b) Stable counting sort of records by a small integer key (the building block
of radix sort).
(c) Bucket sort floats uniformly spread in [0, 1).
(d) Interview application: return the k most frequent values, ties broken by
smaller value, in O(n) using frequency buckets.

Examples
--------
>>> solve([4, -1, 2, 4, 0, -1])
[-1, -1, 0, 2, 4, 4]
>>> top_k_frequent([1, 1, 1, 2, 2, 3], 2)
[1, 2]

Constraints
-----------
- Counting sort is sensible when k = O(n). With k = 10^9 it is a disaster.

Approach ladder
---------------
1. Comparison sort — sorted(), O(n log n). Comparison sorts cannot beat
   Omega(n log n) in the worst case (decision-tree argument).
2. Improved   — if keys are small integers, count occurrences and write them
   back in order: O(n + k), no comparisons at all.
3. Stable version — prefix-sum the counts to get each key's starting slot,
   then place records left to right. Stability is what radix sort relies on.

Follow-ups
----------
- Bucket sort worst case: everything lands in one bucket -> cost of the inner sort.
- Top-k frequent with a heap is O(n log k); bucket version is O(n).
- Sort characters of a string by frequency: same bucket idea.
"""
from __future__ import annotations

from collections import Counter


def solve(nums: list[int]) -> list[int]:
    """Simple counting sort with offset for negatives. O(n + k)."""
    if not nums:
        return []
    lo, hi = min(nums), max(nums)
    counts = [0] * (hi - lo + 1)
    for x in nums:
        counts[x - lo] += 1
    out = []
    for offset, c in enumerate(counts):
        out.extend([offset + lo] * c)
    return out


def counting_sort_stable(records: list, key, k: int) -> list:
    """Stable sort of records by key(record) in range [0, k)."""
    counts = [0] * k
    for r in records:
        counts[key(r)] += 1
    starts, total = [0] * k, 0
    for v in range(k):                       # exclusive prefix sum: first slot of each key
        starts[v] = total
        total += counts[v]
    out = [None] * len(records)
    for r in records:                        # left to right keeps equal keys in order
        out[starts[key(r)]] = r
        starts[key(r)] += 1
    return out


def bucket_sort(values: list[float], n_buckets: int | None = None) -> list[float]:
    """For floats in [0, 1). Expected O(n) when values are spread uniformly."""
    if not values:
        return []
    n_buckets = n_buckets or len(values)
    buckets: list[list[float]] = [[] for _ in range(n_buckets)]
    for v in values:
        buckets[min(int(v * n_buckets), n_buckets - 1)].append(v)
    out = []
    for b in buckets:
        out.extend(sorted(b))                # tiny buckets; insertion sort in textbooks
    return out


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    freq = Counter(nums)
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]
    for value, f in freq.items():
        buckets[f].append(value)
    out: list[int] = []
    for f in range(len(buckets) - 1, 0, -1):
        for value in sorted(buckets[f]):     # deterministic tie-break: smaller value first
            out.append(value)
            if len(out) == k:
                return out
    return out


def main() -> None:
    data = [4, -1, 2, 4, 0, -1, 3]
    print("counting sort:", solve(data), "| matches sorted():", solve(data) == sorted(data))
    lo = min(data)
    counts = [0] * (max(data) - lo + 1)
    for x in data:
        counts[x - lo] += 1
    print("count array (value: count):", {v + lo: c for v, c in enumerate(counts)})
    students = [("ann", 2), ("bob", 0), ("cat", 2), ("dan", 1), ("eve", 0)]
    print("stable by grade:", counting_sort_stable(students, key=lambda r: r[1], k=3))
    vals = [0.78, 0.17, 0.39, 0.26, 0.72, 0.94, 0.21, 0.12, 0.23, 0.68]
    print("bucket sort:", bucket_sort(vals))
    print("top 2 frequent:", top_k_frequent([1, 1, 1, 2, 2, 3], 2))
    print("top 2 frequent with tie:", top_k_frequent([5, 5, 7, 7, 9], 2))
    print("edge cases:", solve([]), solve([3]), solve([2, 2, 2]), bucket_sort([]))


if __name__ == "__main__":
    main()
