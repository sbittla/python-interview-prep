"""
Exercise 053 — Interleave a List With Its Reverse                [Tier: ◆ Extended]
Chapter 45 · Linked lists · Intermediate · Pattern: Find middle + reverse + merge · Target time: 20 min

Problem
-------
A list holds nodes L0 -> L1 -> ... -> Ln. Rewire it in place into the order
L0 -> Ln -> L1 -> Ln-1 -> L2 -> ... (first, last, second, second-last, ...).
Change pointers only; do not change values. Return nothing; mutate the list.
(Resembles "Reorder List".)

Examples
--------
`reordered(values)` builds the list, calls `solve`, and returns the values.

>>> reordered([1, 2, 3, 4])
[1, 4, 2, 3]
>>> reordered([1, 2, 3, 4, 5])
[1, 5, 2, 4, 3]
>>> reordered([])
[]

Constraints
-----------
- 0 <= number of nodes <= 5 * 10^4
- O(1) extra space for the optimal version.

Hidden edge cases
-----------------
- Empty list, one node, two nodes (already in final order).
- Odd vs even length: the middle node must end up last with `next = None`.
- Forgetting to cut the first half creates a cycle.

Hints
-----
1. The second half, read backwards, is exactly the sequence you interleave.
2. Three classic sub-routines solve it: find the middle, reverse a list, merge alternately.

Approach ladder
---------------
1. Brute force — copy node references into a Python list and use two indices from both
   ends to rewire. O(n) time, O(n) space.
2. Optimal — slow/fast pointers find the middle, cut, reverse the second half in place,
   then zip the halves together. O(n) time, O(1) space. We move up to remove the O(n)
   array, which is what the interviewer is testing.

Complexity
----------
Optimal: O(n) time, O(1) extra space.

Follow-ups
----------
- Check whether a list is a palindrome in O(1) space (same middle + reverse steps).
- Restore the second half afterwards so the caller's list is unchanged.
- Do it for a doubly linked list (no reversal needed).

Common wrong answers
--------------------
- Not setting the first half's tail `next` to None, leaving a cycle.
- Choosing the wrong middle for even lengths, so one half is two nodes longer.
- Swapping values instead of nodes (violates the statement).
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


def brute_force(head: ListNode | None) -> None:
    """Array of node references; rewire with two indices."""
    nodes = []
    while head:
        nodes.append(head)
        head = head.next
    i, j = 0, len(nodes) - 1
    order = []
    while i <= j:
        order.append(nodes[i])
        if i != j:
            order.append(nodes[j])
        i, j = i + 1, j - 1
    for a, b in zip(order, order[1:]):
        a.next = b
    if order:
        order[-1].next = None


def _reverse(head: ListNode | None) -> ListNode | None:
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next
    return prev


def solve(head: ListNode | None) -> None:
    """Middle, reverse second half, merge alternately — all in place."""
    if not head or not head.next:
        return
    slow, fast = head, head.next
    while fast and fast.next:          # slow stops at end of first half
        slow, fast = slow.next, fast.next.next
    second = _reverse(slow.next)
    slow.next = None                   # cut: prevents a cycle
    first = head
    while second:
        nxt1, nxt2 = first.next, second.next
        first.next, second.next = second, nxt1
        first, second = nxt1, nxt2


def reordered(values: list[int], fn=None) -> list[int]:
    head = build(values)
    (fn or solve)(head)
    return to_list(head)


# Minimal interview version
def interview_version(head):
    if not head:
        return
    slow = fast = head
    while fast.next and fast.next.next:
        slow, fast = slow.next, fast.next.next
    prev, cur = None, slow.next
    slow.next = None
    while cur:
        cur.next, prev, cur = prev, cur, cur.next
    a, b = head, prev
    while b:
        a.next, b.next, a, b = b, a.next, a.next, b.next


def main() -> None:
    for values in ([1, 2, 3, 4], [1, 2, 3, 4, 5], [], [1], [1, 2], list(range(10))):
        print(f"reorder {values} -> {reordered(values)}")
    print(f"interview version: {reordered([1, 2, 3, 4, 5, 6], interview_version)}")


if __name__ == "__main__":
    main()
