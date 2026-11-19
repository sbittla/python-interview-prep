"""
Exercise 08 — Partition a List Around x (stable)                [Tier: ★ Core]
Chapter 13 · Pattern: two dummy heads · Target time: 15 min

Problem
-------
Given a singly linked list and a value x, reorder it so every node with value < x
comes before every node with value >= x. Both groups keep their original relative
order. Reuse the nodes and return the new head.

Examples
--------
>>> to_list(solve(build([1, 4, 3, 2, 5, 2]), 3))
[1, 2, 2, 4, 3, 5]

Constraints
-----------
- 0 <= n <= 10**5; values and x are ints (may be negative).

Hints
-----
- Build two lists as you walk: "less" and "rest", each with its own dummy head.
- Glue less_tail.next = rest_dummy.next, and terminate rest_tail.next = None.

Edge cases
----------
- Empty list; all values < x; none < x; x smaller/larger than every value.

Wrong-but-tempting
------------------
- Forgetting rest_tail.next = None: the last "rest" node may still point into the
  "less" chain, creating a cycle (to_list then hangs or raises).
"""
from __future__ import annotations

from listnode import ListNode, build, render, to_list


def brute_force(head: ListNode | None, x: int) -> ListNode | None:
    raise NotImplementedError("TODO")


def solve(head: ListNode | None, x: int) -> ListNode | None:
    raise NotImplementedError("TODO")


def forgot_terminator(head: ListNode | None, x: int) -> ListNode | None:
    """The tempting bug: identical except rest_tail.next is never cleared."""
    less = less_tail = ListNode()
    rest = rest_tail = ListNode()
    while head is not None:
        if head.val < x:
            less_tail.next = head
            less_tail = head
        else:
            rest_tail.next = head
            rest_tail = head
        head = head.next
    less_tail.next = rest.next
    return less.next


def main() -> None:
    for vals, x in [([1, 4, 3, 2, 5, 2], 3), ([2, 1], 2), ([5, 6], 1), ([1, 2], 9), ([], 0)]:
        print(f"{vals!s:<20} x={x} -> {render(solve(build(vals), x))}")
    try:
        to_list(forgot_terminator(build([3, 1]), 2), limit=100)
    except ValueError as e:
        print("forgot rest_tail.next = None ->", e)


if __name__ == "__main__":
    main()
