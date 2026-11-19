"""
Exercise 07 — Odd-Even Regroup                                  [Tier: ★ Core]
Chapter 13 · Pattern: two running tails · Target time: 15 min

Problem
-------
Rearrange a singly linked list so that all nodes at odd POSITIONS (1st, 3rd, 5th,
...; 1-based) come first, followed by all nodes at even positions. Keep the
relative order inside each group. Reuse the nodes; O(1) extra space.

Examples
--------
>>> to_list(solve(build([1, 2, 3, 4, 5])))
[1, 3, 5, 2, 4]
>>> to_list(solve(build([2, 1, 3, 5, 6, 4, 7])))
[2, 3, 6, 7, 1, 5, 4]

Constraints
-----------
- 0 <= n <= 10**5. Positions matter, not values.

Hints
-----
- Keep `odd` and `even` tails, plus `even_head` so you can glue the groups at the end.
- Each step: odd.next = even.next; odd = odd.next; even.next = odd.next; even = even.next.
- Loop while `even` and `even.next` exist.

Approach ladder
---------------
1. Brute force — slice the values ([0::2] + [1::2]) and rebuild. O(n) space, new nodes.
2. Optimal    — weave two sublists in one pass, then link odd tail -> even head.
   O(n) time, O(1) space.

Edge cases
----------
- 0, 1, 2 nodes; odd and even lengths.

Wrong-but-tempting
------------------
- Grouping by VALUE parity instead of position.
- Assuming the even tail is terminated without checking: here it is, because the
  last `even.next = odd.next` copies a None — verify that on paper for odd and
  even lengths.
"""
from __future__ import annotations

from listnode import ListNode, build, render, to_list


def brute_force(head: ListNode | None) -> ListNode | None:
    vals = to_list(head)
    return build(vals[0::2] + vals[1::2])


def solve(head: ListNode | None) -> ListNode | None:
    if head is None:
        return None
    odd, even = head, head.next
    even_head = even
    while even is not None and even.next is not None:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = even_head
    return head


def main() -> None:
    for vals in ([1, 2, 3, 4, 5], [2, 1, 3, 5, 6, 4, 7], [1, 2], [1], []):
        print(f"{vals!s:<22} -> {render(solve(build(vals)))}")


if __name__ == "__main__":
    main()
