"""
Exercise 01 — Linked-List Toolkit: length, insert, delete, reverse     [Tier: ★ Core]
Chapter 13 · Pattern: pointer walking, dummy head · Target time: 20 min

Problem
-------
Using `ListNode` from `listnode.py`, write the four operations every later exercise
leans on. Positions are 0-based; every function returns the (possibly new) head.

- length(head)               number of nodes.
- insert_at(head, i, val)    insert a new node so it ends up at position i
                             (0 <= i <= length); raise IndexError otherwise.
- delete_at(head, i)         unlink the node at position i (0 <= i < length);
                             raise IndexError otherwise.
- reverse(head)              reverse in place, O(1) extra space.
- reverse_recursive(head)    same result, written recursively (O(n) call stack).

Examples
--------
>>> to_list(insert_at(build([1, 3]), 1, 2))
[1, 2, 3]
>>> to_list(delete_at(build([1, 2, 3]), 0))
[2, 3]
>>> to_list(reverse(build([1, 2, 3])))
[3, 2, 1]

Constraints
-----------
- 0 <= n <= 10**5. Values are ints.

Hints
-----
- A dummy node in front of head makes "insert/delete at position 0" the same code
  path as every other position.
- To reverse, keep three names: prev, cur, nxt. Save cur.next BEFORE overwriting it.
- Recursive reverse: reverse the rest, then make head.next point back at head and
  set head.next = None (forgetting that line leaves a 2-node cycle).

Edge cases
----------
- Empty list; i == length (append); i out of range (negative or too large);
  single node reversal; 10**5-node reversal.

Follow-ups
----------
- Reverse only positions left..right in one pass.
- Insert into a sorted list (walk while next.val < val).
"""
from __future__ import annotations

import sys

from listnode import ListNode, build, render, to_list


def length(head: ListNode | None) -> int:
    raise NotImplementedError("TODO")


def brute_force_insert(head: ListNode | None, i: int, val: int) -> ListNode | None:
    raise NotImplementedError("TODO")


def insert_at(head: ListNode | None, i: int, val: int) -> ListNode | None:
    raise NotImplementedError("TODO")


def delete_at(head: ListNode | None, i: int) -> ListNode | None:
    raise NotImplementedError("TODO")


def reverse(head: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def reverse_recursive(head: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def main() -> None:
    head = build([10, 20, 30])
    print("start          :", render(head), "length", length(head))
    head = insert_at(head, 0, 5)
    print("insert_at(0,5) :", render(head))
    head = insert_at(head, 4, 40)
    print("insert_at(4,40):", render(head))
    head = delete_at(head, 2)
    print("delete_at(2)   :", render(head))
    print("reverse        :", render(reverse(head)))
    print("recursive      :", render(reverse_recursive(build([1, 2, 3]))))
    print("reverse []     :", render(reverse(None)))
    try:
        delete_at(build([1]), 1)
    except IndexError as e:
        print("delete_at([1], 1) -> IndexError", e)
    big = build(range(100_000))
    print("iterative 100000 nodes, new head:", reverse(big).val)
    print("recursion limit:", sys.getrecursionlimit())
    try:
        reverse_recursive(build(range(5_000)))
    except RecursionError:
        print("recursive 5000 nodes -> RecursionError")


if __name__ == "__main__":
    main()
