"""
Exercise 14 — Max-Heap and Tie-Breaking Bugs            [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (heaps) · Target time: 10 min

Problem
-------
1. `top_k_largest(nums, k)` must return the k largest numbers in descending order.
   The buggy version pushes the numbers into a `heapq` heap and pops k times —
   but `heapq` is a MIN-heap, so it returns the k smallest.
2. `run_jobs(jobs)` gets `(priority, job_dict)` pairs and must return the job
   names in priority order (lower number first), with equal priorities in
   arrival order. The buggy version pushes `(priority, job_dict)` tuples; when
   two priorities tie, tuple comparison moves on to compare the dicts and raises
   `TypeError: '<' not supported between instances of 'dict' and 'dict'`.

Examples
--------
>>> top_k_largest([5, 1, 9, 3, 7], 2)
[9, 7]
>>> run_jobs([(2, {"name": "b"}), (1, {"name": "a"}), (2, {"name": "c"})])
['a', 'b', 'c']

Constraints
-----------
- 0 <= k <= len(nums) <= 10**5

Approach ladder
---------------
1. Buggy  — min-heap used as max-heap; payload compared on ties.
2. Fixed  — push `-x` and negate on the way out (or `heapq.nlargest`); push
   `(priority, seq, payload)` where `seq` is a unique, increasing counter, so the
   comparison never reaches the payload and ties come out FIFO.
3. Better top-k — keep a size-k MIN-heap of the largest seen: O(n log k) time,
   O(k) space (this is what `heapq.nlargest` does).

Follow-ups
----------
- Negation trick for strings? (Does not work — wrap in a class with reversed `__lt__`.)
- Python 3.14 adds `heapq.heappush_max` and friends (flag: 3.14+ only).
"""
from __future__ import annotations

import heapq
import itertools
from typing import Any


def buggy_top_k_largest(nums: list[int], k: int) -> list[int]:
    heap: list[int] = []
    for x in nums:
        heapq.heappush(heap, x)
    return [heapq.heappop(heap) for _ in range(k)]


def buggy_run_jobs(jobs: list[tuple[int, dict[str, Any]]]) -> list[str]:
    heap: list[tuple[int, dict[str, Any]]] = []
    for priority, job in jobs:
        heapq.heappush(heap, (priority, job))
    return [heapq.heappop(heap)[1]["name"] for _ in range(len(heap))]


def top_k_largest(nums: list[int], k: int) -> list[int]:
    """Size-k min-heap of the largest values: O(n log k)."""
    if k == 0:
        return []
    heap: list[int] = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    return sorted(heap, reverse=True)


def run_jobs(jobs: list[tuple[int, dict[str, Any]]]) -> list[str]:
    """(priority, sequence, payload): ties broken by arrival, payload never compared."""
    counter = itertools.count()
    heap: list[tuple[int, int, dict[str, Any]]] = []
    for priority, job in jobs:
        heapq.heappush(heap, (priority, next(counter), job))
    return [heapq.heappop(heap)[2]["name"] for _ in range(len(heap))]


def main() -> None:
    nums = [5, 1, 9, 3, 7]
    print("buggy top 2:", buggy_top_k_largest(nums, 2))
    print("fixed top 2:", top_k_largest(nums, 2))
    print("negation max-heap pop:", -heapq.heappop([-x for x in sorted(nums)]))
    jobs = [(2, {"name": "b"}), (1, {"name": "a"}), (2, {"name": "c"})]
    try:
        buggy_run_jobs(jobs)
    except TypeError as exc:
        print("buggy run_jobs:", type(exc).__name__, "-", exc)
    print("fixed run_jobs:", run_jobs(jobs))


if __name__ == "__main__":
    main()
