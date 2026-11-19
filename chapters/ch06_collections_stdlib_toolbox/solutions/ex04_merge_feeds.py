"""
Exercise 04 — Merge Sorted Feeds and a Running k-th Largest   [Tier: ★ Core]
Chapter 06 · Pattern: heapq k-way merge, size-k min-heap · Target time: 20 min

Problem
-------
1. `merge_feeds(feeds)` — each feed is a list of (timestamp, message) tuples
   already sorted ascending. Return one list with every item, sorted by
   (timestamp, message). Do not sort the concatenation.
2. `running_kth_largest(stream, k)` — after each number arrives, report the
   k-th largest value seen so far, or None while fewer than k values arrived.

Examples
--------
>>> merge_feeds([[(1, "a"), (5, "e")], [(2, "b")], []])
[(1, 'a'), (2, 'b'), (5, 'e')]
>>> running_kth_largest([5, 1, 7, 3, 9], 2)
[None, 1, 5, 5, 7]

Constraints
-----------
- k feeds with N items in total; stream length n; 1 <= k.

Approach ladder
---------------
Merge:
1. Brute force — concatenate and sort: O(N log N); ignores the existing order.
2. Optimal    — heap of (item, feed_index, position) holding one head per feed:
   O(N log k). `heapq.merge(*feeds)` does the same lazily in one line.
k-th largest:
1. Brute force — sort everything seen after each arrival: O(n^2 log n).
2. Optimal    — keep only the k largest in a MIN-heap; its root is the answer.
   `heappushpop` replaces the root when a bigger value arrives: O(n log k).

Hints
-----
- Tuples compare field by field, so put the sort key first and a tie-breaker
  (feed index) second; the payload never needs comparing (→ §7.20).
- heapq is a min-heap only; "k largest" wants a min-heap of size k.

Follow-ups
----------
- Feeds are infinite generators: `heapq.merge` is lazy; your loop can yield.
- Merge with a key (`heapq.merge(*feeds, key=...)`) or in reverse (`reverse=True`).
"""
from __future__ import annotations

import heapq

Item = tuple[int, str]


def brute_force_merge(feeds: list[list[Item]]) -> list[Item]:
    return sorted(item for feed in feeds for item in feed)


def merge_feeds(feeds: list[list[Item]]) -> list[Item]:
    heap = [(feed[0], i, 0) for i, feed in enumerate(feeds) if feed]
    heapq.heapify(heap)                                   # O(k)
    out: list[Item] = []
    while heap:
        item, i, pos = heapq.heappop(heap)                # O(log k)
        out.append(item)
        if pos + 1 < len(feeds[i]):
            heapq.heappush(heap, (feeds[i][pos + 1], i, pos + 1))
    return out


def merge_with_stdlib(feeds: list[list[Item]]) -> list[Item]:
    return list(heapq.merge(*feeds))


def brute_force_kth(stream: list[int], k: int) -> list[int | None]:
    seen: list[int] = []
    out: list[int | None] = []
    for x in stream:
        seen.append(x)
        out.append(sorted(seen, reverse=True)[k - 1] if len(seen) >= k else None)
    return out


def running_kth_largest(stream: list[int], k: int) -> list[int | None]:
    heap: list[int] = []                                  # the k largest so far
    out: list[int | None] = []
    for x in stream:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heappushpop(heap, x)                    # push then pop the min
        out.append(heap[0] if len(heap) == k else None)
    return out


def main() -> None:
    feeds = [[(1, "boot"), (4, "login"), (9, "logout")],
             [(2, "cron"), (4, "alert")],
             [],
             [(3, "deploy")]]
    merged = merge_feeds(feeds)
    print("merged:", merged)
    print("same as sort:", merged == brute_force_merge(feeds),
          "| same as heapq.merge:", merged == merge_with_stdlib(feeds))
    stream = [5, 1, 7, 3, 9, 9, 2]
    print("running 3rd largest:", running_kth_largest(stream, 3))
    print("matches brute force:", running_kth_largest(stream, 3) == brute_force_kth(stream, 3))
    nums = [5, 1, 7, 3, 9, 2]
    heapq.heapify(nums)
    print("heapify ->", nums, "| root =", nums[0])
    print("nlargest(2) =", heapq.nlargest(2, nums), "| nsmallest(2) =", heapq.nsmallest(2, nums))
    words = ["kiwi", "fig", "banana", "apple"]
    print("nlargest(2, key=len) =", heapq.nlargest(2, words, key=len))


if __name__ == "__main__":
    main()
