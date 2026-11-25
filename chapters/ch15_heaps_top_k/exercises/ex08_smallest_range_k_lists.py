"""
Exercise 08 — Smallest Range Covering K Sorted Lists               [Tier: ◆ Extended]
Chapter 15 · Pattern: k-way merge heap + running maximum · Target time: 30 min

Problem
-------
Given k non-empty lists of integers, each sorted ascending, return the smallest range
[lo, hi] that contains at least one number from every list. A range is smaller if
hi - lo is smaller; on equal width the one with the smaller lo wins.

Examples
--------
>>> solve([[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]])
(20, 24)
>>> solve([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
(1, 1)

Constraints
-----------
- 1 <= k; every list non-empty and sorted; N numbers in total.
- An empty list (no range can cover it) raises ValueError in every rung.

Hints
-----
- The heap gives the minimum cheaply; track the maximum in a plain variable, it only
  grows as pointers advance.
- Compare candidates by the tuple (hi - lo, lo).

Follow-ups
----------
- Lists are lazy, finite iterators: keep the iterator per list instead of an index; it still
  stops when any one runs out (infinite sources never terminate).
- Find the range covering at least m of the k lists: the sliding-window rung adapts,
  the heap rung does not.

Wrong-but-tempting
------------------
- Popping from the list holding the MAXIMUM: the max can only grow, so the range never
  shrinks; you must advance the minimum.
- Continuing after one list is exhausted by dropping it: the range must cover ALL lists.
"""
from __future__ import annotations

import bisect
import heapq
import random
from collections import defaultdict


def _check(lists: list[list[int]]) -> None:
    raise NotImplementedError("TODO")


def brute_force(lists: list[list[int]]) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def by_window(lists: list[list[int]]) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def solve(lists: list[list[int]]) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [[[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]],
             [[1, 2, 3], [1, 2, 3], [1, 2, 3]],
             [[1, 9], [4, 12], [7, 10, 16]],
             [[5]],
             [[-5, -1], [10]]]
    for lists in cases:
        ans = solve(lists)
        print(f"{lists} -> {ans}  agree={ans == brute_force(lists) == by_window(lists)}")
    for fn in (brute_force, by_window, solve):
        try:
            fn([[1, 2], []])
        except ValueError as e:
            print(f"{fn.__name__:<11} on an empty list -> ValueError: {e}")
    rng = random.Random(15)
    ok = True
    for _ in range(400):
        lists = [sorted(rng.randint(0, 15) for _ in range(rng.randint(1, 5)))
                 for _ in range(rng.randint(1, 4))]
        ok &= solve(lists) == brute_force(lists) == by_window(lists)
    print("400 random cases (duplicates, ties) agree:", ok)


if __name__ == "__main__":
    main()
