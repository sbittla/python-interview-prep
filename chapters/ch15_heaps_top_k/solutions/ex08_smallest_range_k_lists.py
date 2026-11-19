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

Approach ladder
---------------
1. Brute force — the best range starts at some value lo in the input. For each lo, the
   smallest valid hi is max over lists of (first element >= lo), found by bisect; skip lo
   if some list has none. O(N * k log m) time.
2. Improved   — merge everything into (value, list_id) pairs, sort, then a sliding window
   that covers all k list ids (like "minimum window substring"). O(N log N) time, O(N) space.
3. Optimal    — one pointer per list in a min-heap of (value, list_id, index), plus the
   running maximum of the heap. Each step: [heap min, max] is a candidate; pop the min and
   advance its list; stop when any list runs out (no later range can cover it).
   O(N log k) time, O(k) space.
   Why move up: rung 2 sorts all N values; the heap only ever holds k.

Hints
-----
- The heap gives the minimum cheaply; track the maximum in a plain variable, it only
  grows as pointers advance.
- Compare candidates by the tuple (hi - lo, lo).

Follow-ups
----------
- Lists are infinite generators: the heap version works unchanged (stop on exhaustion).
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
    if not lists or any(not lst for lst in lists):
        raise ValueError("need at least one list and no empty lists")


def brute_force(lists: list[list[int]]) -> tuple[int, int]:
    _check(lists)
    best = None
    for lo in sorted({v for lst in lists for v in lst}):
        hi = lo
        for lst in lists:
            i = bisect.bisect_left(lst, lo)
            if i == len(lst):
                break                                  # some list has nothing >= lo
            hi = max(hi, lst[i])
        else:
            if best is None or (hi - lo, lo) < (best[1] - best[0], best[0]):
                best = (lo, hi)
    return best


def by_window(lists: list[list[int]]) -> tuple[int, int]:
    _check(lists)
    pairs = sorted((v, i) for i, lst in enumerate(lists) for v in lst)
    need, have = len(lists), defaultdict(int)
    covered, left, best = 0, 0, None
    for v, i in pairs:
        have[i] += 1
        covered += have[i] == 1
        while covered == need:                         # shrink from the left
            lo = pairs[left][0]
            if best is None or (v - lo, lo) < (best[1] - best[0], best[0]):
                best = (lo, v)
            j = pairs[left][1]
            have[j] -= 1
            covered -= have[j] == 0
            left += 1
    return best


def solve(lists: list[list[int]]) -> tuple[int, int]:
    _check(lists)
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists)]
    heapq.heapify(heap)
    hi = max(lst[0] for lst in lists)
    best = (heap[0][0], hi)
    while True:
        lo, i, j = heap[0]
        if hi - lo < best[1] - best[0]:                # equal width: earlier lo already kept
            best = (lo, hi)
        if j + 1 == len(lists[i]):
            return best                                # list i exhausted
        nxt = lists[i][j + 1]
        hi = max(hi, nxt)
        heapq.heapreplace(heap, (nxt, i, j + 1))


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
