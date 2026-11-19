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
        raise NotImplementedError("TODO")

    def __len__(self) -> int:
        raise NotImplementedError("TODO")

    def peek(self) -> Any:
        raise NotImplementedError("TODO")

    def push(self, x: Any) -> None:
        raise NotImplementedError("TODO")

    def pop(self) -> Any:
        raise NotImplementedError("TODO")

    def pushpop(self, x: Any) -> Any:
        raise NotImplementedError("TODO")

    def replace(self, x: Any) -> Any:
        raise NotImplementedError("TODO")

    def as_list(self) -> list[Any]:
        raise NotImplementedError("TODO")

    def _swap(self, i: int, j: int) -> None:
        raise NotImplementedError("TODO")

    def _sift_up(self, i: int) -> None:
        raise NotImplementedError("TODO")

    def _sift_down(self, i: int) -> None:
        raise NotImplementedError("TODO")


def is_min_heap(a: list[Any]) -> bool:
    raise NotImplementedError("TODO")


def brute_force(items: Iterable[Any]) -> list[Any]:
    """Rung 1: unsorted list, pop scans for the minimum. O(n^2) to drain."""
    raise NotImplementedError("TODO")


def build_by_pushes(items: Iterable[Any]) -> MinHeap:
    """Rung 2: n pushes, O(n log n) build."""
    raise NotImplementedError("TODO")


def solve(items: Iterable[Any]) -> list[Any]:
    """Rung 3: O(n) heapify, then n pops: O(n log n) heap sort."""
    raise NotImplementedError("TODO")


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
