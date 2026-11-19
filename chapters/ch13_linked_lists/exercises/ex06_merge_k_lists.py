"""
Exercise 06 — Merge k Sorted Lists                               [Tier: ★ Core]
Chapter 13 · Pattern: dummy tail + min-heap (→ Ch 15) · Target time: 25 min

Problem
-------
You get a Python list of k heads; each linked list is sorted ascending (some may be
empty). Splice all nodes into ONE ascending list and return its head. Reuse the
existing nodes. Equal values keep their input order: a node from an earlier list
comes before an equal node from a later list (stable merge).

Examples
--------
>>> to_list(solve([build([1, 4, 5]), build([1, 3, 4]), build([2, 6])]))
[1, 1, 2, 3, 4, 4, 5, 6]
>>> to_list(solve([])), to_list(solve([None, None]))
([], [])

Constraints
-----------
- 0 <= k <= 10**4; N = total nodes <= 10**5.

Hints
-----
- Two-list merge: keep a dummy node and a `tail`; append the smaller head each step.
- k lists: a heap holding one head per list gives the global minimum in O(log k).
- ListNode is not orderable. Push (val, list_index, node): the index breaks ties
  BEFORE Python ever tries to compare two nodes — and it makes the merge stable.

Edge cases
----------
- k = 0; all lists empty; one list; many duplicates across lists.

Wrong-but-tempting
------------------
- heapq.heappush(h, (node.val, node)): TypeError on the first tie, because Python
  then compares two ListNode objects.
- Forgetting to push node.next after popping node.

Follow-ups
----------
- k sorted ARRAYS or iterators: heapq.merge does this lazily (Ch 15).
- Lists too large for memory: the same heap over file readers (external merge sort).
"""
from __future__ import annotations

import heapq
import random

from listnode import ListNode, build, to_list


def merge_two(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def brute_force(heads: list[ListNode | None]) -> ListNode | None:
    raise NotImplementedError("TODO")


def one_by_one(heads: list[ListNode | None]) -> ListNode | None:
    raise NotImplementedError("TODO")


def divide_and_conquer(heads: list[ListNode | None]) -> ListNode | None:
    raise NotImplementedError("TODO")


def solve(heads: list[ListNode | None]) -> ListNode | None:
    raise NotImplementedError("TODO")


def main() -> None:
    demo = [[1, 4, 5], [1, 3, 4], [2, 6]]
    print("heap      :", to_list(solve([build(x) for x in demo])))
    print("one_by_one:", to_list(one_by_one([build(x) for x in demo])))
    print("divide    :", to_list(divide_and_conquer([build(x) for x in demo])))
    print("brute     :", to_list(brute_force([build(x) for x in demo])))
    print("empty     :", to_list(solve([])), to_list(solve([None, build([])])))
    a, b = ListNode(1), ListNode(1)       # equal values: stability check
    first = solve([a, b])
    print("stable    :", first is a and first.next is b)
    try:
        heapq.heapify([(1, ListNode(1)), (1, ListNode(1))])
    except TypeError as e:
        print("(val, node) tuples ->", type(e).__name__)
    rng = random.Random(6)
    lists = [sorted(rng.randint(0, 50) for _ in range(rng.randint(0, 30))) for _ in range(20)]
    merged = to_list(solve([build(x) for x in lists]))
    print("20 random lists ok:", merged == sorted(v for x in lists for v in x), len(merged), "nodes")


if __name__ == "__main__":
    main()
