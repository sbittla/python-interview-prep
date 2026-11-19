"""
Exercise 01 — Array-Backed Min-Heap From Scratch                   [Tier: ★ Core]
Chapter 15 · Pattern: binary heap in a list (sift up / sift down / heapify) · Target time: 25 min

Problem
-------
Implement a `MinHeap` class backed by a plain Python list, without `heapq`:

- `MinHeap(items)` builds the heap from any iterable in O(n) (bottom-up heapify).
- `push(x)`, `pop()`, `peek()`, `__len__`.
- `pushpop(x)`  — push x then pop the minimum, in one sift.
- `replace(x)`  — pop the minimum then push x, in one sift (raises on an empty heap).
- `pop`/`peek`/`replace` on an empty heap raise `IndexError`.

Then use it for `solve(items)`: return the items in ascending order (heap sort by popping).
The class counts element swaps in `self.swaps` so the demo can show why heapify is O(n)
while n pushes are O(n log n).

Examples
--------
>>> h = MinHeap([5, 3, 8, 1]); h.pop(), h.pop(), len(h)
(1, 3, 2)
>>> solve([4, 1, 3, 1])
[1, 1, 3, 4]

Constraints
-----------
- Items are mutually comparable with `<` (numbers, strings, tuples).
- 0 <= n <= 10^5.

Approach ladder
---------------
1. Brute force — keep an unsorted list; `pop` scans for the minimum: push O(1), pop O(n).
   Or keep it sorted: push O(n) (insort), pop O(1). One side is always linear.
2. Improved   — binary heap, built by n pushes: push/pop O(log n); build O(n log n).
3. Optimal    — same heap, but build it bottom-up: sift_down every internal node from the
   last one (index n//2 - 1) to the root. Total work is
   sum over heights h of (n / 2^(h+1)) * h = O(n), because half the nodes are leaves
   (zero work) and only one node has height log n.
   Index formulas (0-based): parent(i) = (i - 1) // 2, children 2i + 1 and 2i + 2.

Hints
-----
- Sift up: while i > 0 and a[i] < a[parent], swap and move up.
- Sift down: pick the SMALLER child; swap only if it is smaller than a[i].
- pop: save a[0], move the last element to index 0, shrink, sift down.
- heapify: range(n // 2 - 1, -1, -1).

Follow-ups
----------
- Max-heap: flip the comparisons, or store negated keys (→ §15.2).
- Decrease-key / remove-arbitrary: keep a dict value -> index, update it on every swap.
- Why does `heapq` use only `<`? So any type defining `__lt__` works (→ §6.8).
- d-ary heaps: shallower tree, cheaper push, costlier pop.

Wrong-but-tempting
------------------
- Sifting down towards the LEFT child always: breaks the heap when the right child is smaller.
- `pop` that removes a[0] with `del a[0]`: O(n) shift AND destroys the parent/child layout.
- Heapify from index 0 upwards with sift_down: children are not heaps yet, so it is wrong.
"""
from __future__ import annotations

import heapq
import random
from typing import Any, Iterable


class MinHeap:
    def __init__(self, items: Iterable[Any] = ()) -> None:
        self._a: list[Any] = list(items)
        self.swaps = 0
        for i in range(len(self._a) // 2 - 1, -1, -1):   # last internal node -> root
            self._sift_down(i)

    def __len__(self) -> int:
        return len(self._a)

    def peek(self) -> Any:
        if not self._a:
            raise IndexError("peek from empty heap")
        return self._a[0]

    def push(self, x: Any) -> None:
        self._a.append(x)
        self._sift_up(len(self._a) - 1)

    def pop(self) -> Any:
        if not self._a:
            raise IndexError("pop from empty heap")
        last = self._a.pop()
        if not self._a:
            return last
        top, self._a[0] = self._a[0], last
        self._sift_down(0)
        return top

    def pushpop(self, x: Any) -> Any:
        if self._a and self._a[0] < x:
            x, self._a[0] = self._a[0], x
            self._sift_down(0)
        return x

    def replace(self, x: Any) -> Any:
        if not self._a:
            raise IndexError("replace on empty heap")
        top, self._a[0] = self._a[0], x
        self._sift_down(0)
        return top

    def as_list(self) -> list[Any]:
        return list(self._a)

    def _swap(self, i: int, j: int) -> None:
        self._a[i], self._a[j] = self._a[j], self._a[i]
        self.swaps += 1

    def _sift_up(self, i: int) -> None:
        a = self._a
        while i > 0:
            parent = (i - 1) // 2
            if not a[i] < a[parent]:
                break
            self._swap(i, parent)
            i = parent

    def _sift_down(self, i: int) -> None:
        a, n = self._a, len(self._a)
        while True:
            child = 2 * i + 1
            if child >= n:
                break
            if child + 1 < n and a[child + 1] < a[child]:
                child += 1                                   # the smaller child
            if not a[child] < a[i]:
                break
            self._swap(i, child)
            i = child


def is_min_heap(a: list[Any]) -> bool:
    return all(not a[i] < a[(i - 1) // 2] for i in range(1, len(a)))


def brute_force(items: Iterable[Any]) -> list[Any]:
    """Rung 1: unsorted list, pop scans for the minimum. O(n^2) to drain."""
    pool, out = list(items), []
    while pool:
        i = min(range(len(pool)), key=pool.__getitem__)
        out.append(pool.pop(i))
    return out


def build_by_pushes(items: Iterable[Any]) -> MinHeap:
    """Rung 2: n pushes, O(n log n) build."""
    h = MinHeap()
    for x in items:
        h.push(x)
    return h


def solve(items: Iterable[Any]) -> list[Any]:
    """Rung 3: O(n) heapify, then n pops: O(n log n) heap sort."""
    h = MinHeap(items)
    return [h.pop() for _ in range(len(h))]


def main() -> None:
    h = MinHeap([9, 4, 7, 1, 8, 2, 6])
    print("heapify [9,4,7,1,8,2,6] ->", h.as_list(), " valid:", is_min_heap(h.as_list()))
    h.push(0)
    print("push 0                  ->", h.as_list())
    print("pop                     ->", h.pop(), h.as_list())
    print("pushpop(5)              ->", h.pushpop(5), h.as_list())
    print("pushpop(-1) (smaller)   ->", h.pushpop(-1), h.as_list())
    print("replace(10)             ->", h.replace(10), h.as_list())
    print("solve [4,1,3,1]         ->", solve([4, 1, 3, 1]))
    print("solve strings           ->", solve(["pear", "fig", "apple"]))
    try:
        MinHeap().pop()
    except IndexError as e:
        print("empty pop               -> IndexError:", e)

    # heapq.heapify sifts to a leaf first, so its layout may differ; both must be valid heaps.
    rng = random.Random(15)
    data = [rng.randint(0, 99) for _ in range(50)]
    ref = list(data)
    heapq.heapify(ref)
    mine = MinHeap(data).as_list()
    print("valid like heapq.heapify ->", is_min_heap(mine) and is_min_heap(ref),
          " same root:", mine[0] == ref[0])

    # Why heapify is O(n): count swaps on the worst case (descending input).
    print("swaps on descending input (n = 2^h - 1):")
    print("      n   heapify   n pushes   heapify/n")
    for height in (7, 10, 13):
        n = 2 ** height - 1
        desc = list(range(n, 0, -1))
        a, b = MinHeap(desc).swaps, build_by_pushes(desc).swaps
        print(f"  {n:>5}   {a:>7}   {b:>8}   {a / n:.2f}")
    print("all rungs agree on 200 random lists:",
          all(solve(xs) == brute_force(xs) == sorted(xs)
              for xs in ([rng.randint(-5, 5) for _ in range(rng.randint(0, 20))]
                         for _ in range(200))))


if __name__ == "__main__":
    main()
