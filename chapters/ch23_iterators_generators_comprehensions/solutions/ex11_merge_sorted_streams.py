"""
Exercise 11 — Lazily Merge K Sorted Streams                   [Tier: ◆ Extended]
Chapter 23 · Pattern: generator + heap · Target time: 20 min

Problem
-------
``merge_sorted(*iterables, key=None)`` takes k iterables, each already sorted, and yields all
items in sorted order. It must be lazy (works on infinite or huge streams) and stable: equal
items come out in the order of the input iterables they came from.

Examples
--------
>>> list(merge_sorted([1, 4, 7], [2, 5], [3, 6, 9]))
[1, 2, 3, 4, 5, 6, 7, 9]

Constraints
-----------
- k up to 10^4 streams, N total items; target O(N log k) time, O(k) memory.
- Items might not be comparable with each other beyond the key (avoid comparing items directly
  on ties).

Hints
-----
- Push ``(key, stream_index, item, iterator)`` onto a heap; the index breaks ties so the item and
  iterator are never compared.
- After popping, pull the next item from the same iterator and push it back.
- ``heapq.merge`` is the standard-library answer; know it exists and write your own anyway.

Approach ladder
---------------
1. Concatenate and sort — O(N log N) time, O(N) memory, not lazy.
2. Repeatedly scan the k heads for the minimum — O(N k), lazy.
3. Min-heap of heads — O(N log k), O(k) memory, lazy.

Follow-ups
----------
- External sort: sort chunks to temp files, then k-way merge them with this function.
- Merge log files from many servers by timestamp (the ``key`` parameter).
"""
from __future__ import annotations

import heapq
from itertools import count, islice
from typing import Callable, Iterable, Iterator

_END = object()  # sentinel: 'iterator exhausted'


def merge_concat_sort(*iterables: Iterable, key: Callable | None = None) -> list:
    return sorted((x for it in iterables for x in it), key=key)


def merge_scan(*iterables: Iterable, key: Callable | None = None) -> Iterator:
    key = key or (lambda x: x)
    sentinel = object()
    iters = [iter(it) for it in iterables]
    heads = [next(it, sentinel) for it in iters]
    while True:
        best = None
        for i, h in enumerate(heads):
            if h is not sentinel and (best is None or key(h) < key(heads[best])):
                best = i
        if best is None:
            return
        yield heads[best]
        heads[best] = next(iters[best], sentinel)


def merge_sorted(*iterables: Iterable, key: Callable | None = None) -> Iterator:
    key = key or (lambda x: x)
    heap = []
    for idx, it in enumerate(map(iter, iterables)):
        for item in it:  # take the first item, if any
            heap.append((key(item), idx, item, it))
            break
    heapq.heapify(heap)
    while heap:
        k, idx, item, it = heap[0]
        yield item
        nxt = next(it, _END)
        if nxt is _END:
            heapq.heappop(heap)
        else:
            heapq.heapreplace(heap, (key(nxt), idx, nxt, it))


def main() -> None:
    a, b, c = [1, 4, 7, 10], [2, 5, 8], [3, 6, 9, 12, 15]
    print("concat+sort:", merge_concat_sort(a, b, c))
    print("scan       :", list(merge_scan(a, b, c)))
    print("heap       :", list(merge_sorted(a, b, c)))
    print("heapq.merge:", list(heapq.merge(a, b, c)))
    print("with empties:", list(merge_sorted([], [1], [], [0, 2])))

    logs1 = [("10:00:01", "web1", "start"), ("10:00:05", "web1", "req")]
    logs2 = [("10:00:01", "web2", "start"), ("10:00:03", "web2", "req")]
    merged = merge_sorted(logs1, logs2, key=lambda r: r[0])
    print("stable merge by timestamp:")
    for rec in merged:
        print("  ", rec)

    evens = (2 * n for n in count())
    odds = (2 * n + 1 for n in count())
    print("infinite streams:", list(islice(merge_sorted(evens, odds), 10)))

    # dicts are not orderable; the index tie-breaker means they are never compared.
    d = merge_sorted([{"t": 1}, {"t": 3}], [{"t": 1}, {"t": 2}], key=lambda r: r["t"])
    print("dicts:", list(d))


if __name__ == "__main__":
    main()
