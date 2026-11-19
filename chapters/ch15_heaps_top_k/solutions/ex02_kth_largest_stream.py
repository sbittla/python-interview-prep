"""
Exercise 02 — K-th Largest in a Stream                             [Tier: ★ Core]
Chapter 15 · Pattern: size-k min-heap · Target time: 15 min

Problem
-------
Design `KthLargest(k, initial)`: it is created with k and some initial numbers, then
receives numbers one at a time through `add(x)`. After every `add`, return the k-th
largest number seen so far (duplicates count separately), or `None` while fewer than k
numbers have arrived. `solve(k, initial, stream)` returns the list of answers.

(Ch 6 ex04 has a one-shot `running_kth_largest` function; here the API is a class that
must also absorb an initial batch, and we compare three designs.)

Examples
--------
>>> solve(3, [4, 5, 8, 2], [3, 5, 10, 9, 4])
[4, 5, 5, 8, 8]
>>> solve(2, [], [7, 7, 1])
[None, 7, 7]

Constraints
-----------
- 1 <= k; up to 10^4 calls to add; values are ints.

Approach ladder
---------------
1. Brute force — keep every number, sort on each add, index [-k]: O(n log n) per add.
2. Improved   — keep a sorted list with `bisect.insort`: O(n) per add (list shift),
   O(1) query. Memory still grows with the stream.
3. Optimal    — keep only the k largest in a MIN-heap. Its root is the k-th largest.
   New x: if heap has < k items push; elif x > root, `heapreplace`. O(log k) per add,
   O(k) memory, and the initial batch costs O(m log k) (or O(m) heapify + pops).
   Why move up: the stream may be unbounded; only the k-sized heap stays bounded.

Hints
-----
- "k-th LARGEST" wants a MIN-heap: the smallest of the k kept values is the answer.
- `heapq.heapreplace(h, x)` pops then pushes in one sift; `heappushpop` pushes first.
- For the initial batch: heapify all of it, then pop until only k remain.

Follow-ups
----------
- k-th smallest in a stream: max-heap of size k (store -x).
- Values can also be deleted: a heap cannot find an arbitrary item; use a sorted container
  or lazy deletion with a counter of "to delete" values.
- Sliding window k-th largest: two heaps with lazy deletion, or a sorted list.

Wrong-but-tempting
------------------
- Using a max-heap of everything and popping k times on each query: O(k log n) per query
  AND it destroys the heap.
- `heappushpop` when the heap already has k items but forgetting the "< k" phase:
  returns a wrong root while the heap is still filling.
"""
from __future__ import annotations

import bisect
import heapq
import random


class KthLargestSort:
    """Rung 1: sort everything after each add."""

    def __init__(self, k: int, initial: list[int]) -> None:
        self.k, self.seen = k, list(initial)

    def add(self, x: int) -> int | None:
        self.seen.append(x)
        return sorted(self.seen)[-self.k] if len(self.seen) >= self.k else None


class KthLargestInsort:
    """Rung 2: keep a sorted list."""

    def __init__(self, k: int, initial: list[int]) -> None:
        self.k, self.seen = k, sorted(initial)

    def add(self, x: int) -> int | None:
        bisect.insort(self.seen, x)
        return self.seen[-self.k] if len(self.seen) >= self.k else None


class KthLargest:
    """Rung 3: min-heap holding the k largest values seen."""

    def __init__(self, k: int, initial: list[int]) -> None:
        self.k = k
        self.heap = list(initial)
        heapq.heapify(self.heap)                     # O(m)
        while len(self.heap) > k:
            heapq.heappop(self.heap)                 # drop the smallest extras

    def add(self, x: int) -> int | None:
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, x)
        elif x > self.heap[0]:
            heapq.heapreplace(self.heap, x)          # evict the old k-th largest
        return self.heap[0] if len(self.heap) == self.k else None


def solve(k: int, initial: list[int], stream: list[int], cls: type = KthLargest) -> list[int | None]:
    tracker = cls(k, initial)
    return [tracker.add(x) for x in stream]


def main() -> None:
    cases = [(3, [4, 5, 8, 2], [3, 5, 10, 9, 4]), (2, [], [7, 7, 1]),
             (1, [-3], [-5, -1, -1]), (4, [1, 1], [1, 2, 0, 3])]
    for k, init, stream in cases:
        ans = solve(k, init, stream)
        agree = ans == solve(k, init, stream, KthLargestSort) == solve(k, init, stream, KthLargestInsort)
        print(f"k={k} initial={init} stream={stream} -> {ans}  agree={agree}")
    rng = random.Random(15)
    big = [rng.randint(0, 10**6) for _ in range(5000)]
    t = KthLargest(10, big[:100])
    for x in big[100:]:
        t.add(x)
    print("heap size after 5000 values with k=10:", len(t.heap),
          "| answer correct:", t.heap[0] == sorted(big)[-10])


if __name__ == "__main__":
    main()
