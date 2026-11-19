"""
Exercise 02 — Delete Every Node Holding a Value                  [Tier: ★ Core]
Chapter 13 · Pattern: dummy head · Target time: 10 min

Problem
-------
Given the head of a singly linked list and a value `x`, unlink every node whose
value equals `x` and return the new head. Keep the remaining nodes (same objects)
in their original order.

Examples
--------
>>> to_list(solve(build([7, 1, 7, 7, 2, 7]), 7))
[1, 2]
>>> to_list(solve(build([7, 7]), 7))
[]

Constraints
-----------
- 0 <= n <= 10**5. O(1) extra space for the optimal answer.

Hints
-----
- The hard case is when the head itself (or the first several nodes) must go.
- Put a dummy node before head. Then every deletion is "prev.next = prev.next.next".
- Only advance `prev` when you did NOT delete: after a deletion the new prev.next
  has not been checked yet.

Edge cases
----------
- Empty list; all nodes match; no node matches; runs of matches at head, middle, tail.

Wrong-but-tempting
------------------
- `prev = prev.next` after every step: skips the node that followed a deleted one,
  so [7, 7] with x=7 leaves one 7.
- Returning `head` instead of `dummy.next` when the head was deleted.

Follow-ups
----------
- Sorted list: delete duplicates so each value appears once / delete every value
  that appears more than once.
- Delete a node given ONLY that node (copy next's value in, unlink next; not the tail).
"""
from __future__ import annotations

from listnode import ListNode, build, nodes, render, to_list


def brute_force(head: ListNode | None, x: int) -> ListNode | None:
    raise NotImplementedError("TODO")


def two_loops(head: ListNode | None, x: int) -> ListNode | None:
    raise NotImplementedError("TODO")


def solve(head: ListNode | None, x: int) -> ListNode | None:
    raise NotImplementedError("TODO")


def main() -> None:
    for vals, x in [([7, 1, 7, 7, 2, 7], 7), ([7, 7], 7), ([1, 2, 3], 9), ([], 1)]:
        print(f"{vals!s:<20} x={x} -> {render(solve(build(vals), x))}")
    head = build([1, 2, 1, 3])
    survivors = [n for n in nodes(head) if n.val != 1]
    print("same node objects kept:", nodes(solve(head, 1)) == survivors)
    print("two_loops agrees:", to_list(two_loops(build([4, 4, 5, 4]), 4)) == [5])


if __name__ == "__main__":
    main()
