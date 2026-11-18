"""
Exercise 056 — Reverse a List in Blocks of k                [Tier: ◆ Extended]
Chapter 45 · Linked lists · Advanced · Pattern: Segment reversal with a dummy head · Target time: 30 min

Problem
-------
Given a singly linked list and a positive integer k, reverse the nodes in each
consecutive block of exactly k nodes. A trailing block with fewer than k nodes stays
in its original order. Rewire nodes; do not swap values; use O(1) extra space.
(Resembles "Reverse Nodes in k-Group".)

Examples
--------
>>> to_list(solve(build([1, 2, 3, 4, 5]), 2))
[2, 1, 4, 3, 5]
>>> to_list(solve(build([1, 2, 3, 4, 5]), 3))
[3, 2, 1, 4, 5]
>>> to_list(solve(build([1, 2, 3]), 1))
[1, 2, 3]

Constraints
-----------
- 0 <= number of nodes <= 5000
- 1 <= k <= 5000 (k may exceed the length)

Hidden edge cases
-----------------
- k = 1 (no change) and k equal to the length (reverse everything).
- k larger than the length (no change).
- Length an exact multiple of k (no leftover block).

Hints
-----
1. Before reversing a block, check that k nodes actually exist.
2. Keep a pointer to the node *before* the block (`group_prev`). After reversing, the
   block's old first node is its new last node and becomes the next `group_prev`.

Approach ladder
---------------
1. Brute force — copy values into an array, reverse each full chunk with slicing,
   rebuild. O(n) time, O(n) space, new nodes (not allowed by the statement).
2. Recursive — reverse the first k nodes, recurse on the rest, attach. O(n) time but
   O(n/k) stack.
3. Optimal — iterative: dummy head, find the k-th node from `group_prev`, reverse the
   block in place, splice it back, advance. O(n) time, O(1) space.

Complexity
----------
Optimal: O(n) time (each node is visited twice: once to count, once to reverse),
O(1) extra space.

Follow-ups
----------
- Also reverse the final short block.
- Reverse alternate blocks (reverse k, skip k, ...).
- Swap nodes in pairs (k = 2) without the general machinery.

Common wrong answers
--------------------
- Reversing the trailing short block.
- Losing the link from the previous block to the new block head.
- Counting k nodes but reversing k + 1 (off-by-one on the stop node).
"""
from __future__ import annotations


class ListNode:
    def __init__(self, val: int = 0, next: ListNode | None = None) -> None:
        self.val = val
        self.next = next


def build(values: list[int]) -> ListNode | None:
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def to_list(head: ListNode | None) -> list[int]:
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def brute_force(head: ListNode | None, k: int) -> ListNode | None:
    """Array slices, rebuilt (allocates new nodes)."""
    vals = to_list(head)
    for start in range(0, len(vals) - k + 1, k):
        vals[start:start + k] = vals[start:start + k][::-1]
    return build(vals)


def solve(head: ListNode | None, k: int) -> ListNode | None:
    """Iterative in-place block reversal."""
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        kth = group_prev
        for _ in range(k):                 # find the block's last node
            kth = kth.next
            if kth is None:
                return dummy.next          # short block: leave it
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:       # reverse the block, pointing its tail at group_next
            cur.next, prev, cur = prev, cur, cur.next
        first = group_prev.next            # old first node is now the block's last
        group_prev.next = kth              # splice the new block head in
        group_prev = first


# Minimal interview version
def interview_version(head, k):
    dummy = gp = ListNode(0, head)
    while True:
        kth = gp
        for _ in range(k):
            kth = kth and kth.next
        if not kth:
            return dummy.next
        nxt, prev, cur = kth.next, kth.next, gp.next
        while cur is not nxt:
            cur.next, prev, cur = prev, cur, cur.next
        gp.next, gp = kth, gp.next


def main() -> None:
    for values, k in [([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], 3), ([1, 2, 3], 1),
                      ([1, 2, 3], 3), ([1, 2], 5), ([], 2), ([1, 2, 3, 4, 5, 6], 2)]:
        print(f"k={k} {values} -> {to_list(solve(build(values), k))}")


if __name__ == "__main__":
    main()
