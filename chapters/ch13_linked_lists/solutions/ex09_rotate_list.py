"""
Exercise 09 — Rotate a List Right by k                          [Tier: ★ Core]
Chapter 13 · Pattern: length, close into a ring, cut · Target time: 15 min

Problem
-------
Rotate a singly linked list to the right by k places: the last k nodes move to the
front, in order. k may be larger than the length (and may be 0). Reuse the nodes.

Examples
--------
>>> to_list(solve(build([1, 2, 3, 4, 5]), 2))
[4, 5, 1, 2, 3]
>>> to_list(solve(build([0, 1, 2]), 4))
[2, 0, 1]

Constraints
-----------
- 0 <= n <= 10**5; 0 <= k <= 2 * 10**9.

Hints
-----
- Only k % n matters. Rotating 2 * 10**9 times one step at a time is too slow.
- One pass finds n and the tail. Link tail -> head (a ring), walk n - k%n - 1 steps
  from head to the new tail, cut after it.

Approach ladder
---------------
1. Brute force — repeat k times: move the last node to the front. O(n*k) time.
2. Improved   — the same with k %= n first. O(n * min(k, n)) = O(n^2) worst case.
3. Optimal    — measure, ring, cut. O(n) time, O(1) space.

Edge cases
----------
- Empty list; one node; k == 0; k a multiple of n; k > n.

Follow-ups
----------
- Rotate left by k (the new tail is k % n - 1 steps from head).
"""
from __future__ import annotations

from listnode import ListNode, build, render


def improved(head: ListNode | None, k: int) -> ListNode | None:
    """Rung 2 (improved): move the last node to the front (k % n) times. O(n * min(k, n))."""
    if head is None or head.next is None:
        return head
    n, cur = 1, head
    while cur.next is not None:
        n, cur = n + 1, cur.next
    for _ in range(k % n):
        prev, cur = None, head
        while cur.next is not None:
            prev, cur = cur, cur.next
        prev.next = None
        cur.next = head
        head = cur
    return head


def solve(head: ListNode | None, k: int) -> ListNode | None:
    if head is None or head.next is None:
        return head
    n, tail = 1, head
    while tail.next is not None:
        n, tail = n + 1, tail.next
    k %= n
    if k == 0:
        return head
    tail.next = head                      # close the ring
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None                  # cut the ring
    return new_head


def main() -> None:
    for vals, k in [([1, 2, 3, 4, 5], 2), ([0, 1, 2], 4), ([1, 2, 3], 3),
                    ([1], 99), ([], 5), ([1, 2, 3, 4, 5], 2_000_000_002)]:
        print(f"{vals!s:<16} k={k:<10} -> {render(solve(build(vals), k))}")


if __name__ == "__main__":
    main()
