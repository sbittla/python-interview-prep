"""
Exercise 10 — Swap Adjacent Pairs (relink, don't copy values)   [Tier: ◆ Extended]
Chapter 13 · Pattern: dummy head + local reversal · Target time: 15 min

Problem
-------
Swap every two adjacent nodes of a singly linked list and return the new head:
1->2->3->4->5 becomes 2->1->4->3->5. A trailing odd node stays where it is. You
must relink NODES; swapping the `val` fields is not allowed.

Examples
--------
>>> to_list(solve(build([1, 2, 3, 4])))
[2, 1, 4, 3]
>>> to_list(solve(build([1, 2, 3])))
[2, 1, 3]

Constraints
-----------
- 0 <= n <= 10**5.

Hints
-----
- With a dummy node, every swap looks the same: prev -> a -> b -> rest becomes
  prev -> b -> a -> rest. That is three pointer writes.
- This is "reverse in groups of k" with k = 2 (the general version is
  chapters/ch45_problem_bank/solutions/ex056_reverse_k_group.py).

Edge cases
----------
- 0, 1, 2, 3 nodes; long lists (recursion depth).

Wrong-but-tempting
------------------
- Writing b.next = a BEFORE a.next = b.next: the second write reads the NEW b.next,
  so a.next = a (a self-loop) and `rest` is lost.
"""
from __future__ import annotations

from listnode import ListNode, build, nodes, render


def recursive(head: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def solve(head: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def main() -> None:
    for vals in ([1, 2, 3, 4], [1, 2, 3, 4, 5], [1], []):
        print(f"{vals!s:<16} -> {render(solve(build(vals)))}")
    head = build([1, 2, 3, 4])
    a, b, c, d = nodes(head)
    print("nodes relinked, not copied:", nodes(solve(head)) == [b, a, d, c])
    print("iterative 100000 nodes ok:", solve(build(range(100_000))).val == 1)
    try:
        recursive(build(range(5_000)))
    except RecursionError:
        print("recursive 5000 nodes -> RecursionError")


if __name__ == "__main__":
    main()
