"""
Exercise 051 — Detect a Cycle and Find Its Entry                [Tier: ★ Core]
Chapter 45 · Linked lists · Beginner · Pattern: Fast and slow pointers · Target time: 12 min

Problem
-------
A singly linked list may loop back on itself: some node's `next` points to an earlier
node. Return the node where the cycle begins, or None if the list ends normally.
Use O(1) extra memory in the optimal version.
(Resembles "Linked List Cycle II".)

Examples
--------
Lists are built with `build(values, pos)`: the tail links back to index `pos`
(pos = -1 means no cycle). `entry_index` reports the index of the returned node.

>>> head = build([3, 2, 0, -4], pos=1)
>>> entry_index(head, solve(head))
1
>>> head = build([1, 2], pos=0)
>>> entry_index(head, solve(head))
0
>>> solve(build([1, 2, 3], pos=-1)) is None
True

Constraints
-----------
- 0 <= number of nodes <= 10^4
- -1 <= pos < number of nodes
- Values may repeat, so compare node identity, never values.

Hidden edge cases
-----------------
- Empty list or a single node without a cycle.
- A single node pointing to itself (pos = 0, length 1).
- Cycle that covers the whole list (entry is the head).
- Duplicate values: a value-based "seen" set gives wrong answers.

Hints
-----
1. A pointer that moves two steps for every one step of another must eventually lap it
   inside a loop.
2. After they meet, restart one pointer from the head and move both one step at a time.
   Count distances to see why they meet at the entry.

Approach ladder
---------------
1. Brute force — walk the list storing node identities in a set; the first node seen
   twice is the entry. O(n) time, O(n) space.
2. Optimal — Floyd's tortoise and hare. If slow travels a + b to the meeting point,
   fast travels 2(a + b) = a + b + k*L, so a = k*L - b: a pointer from the head and one
   from the meeting point meet exactly at the entry. O(n) time, O(1) space. We move up
   to drop the hash set.

Complexity
----------
Optimal: O(n) time, O(1) extra space.

Follow-ups
----------
- Return the cycle length (keep one pointer fixed after meeting and count steps).
- Find the duplicate in an array of n+1 numbers in range 1..n using the same trick.
- Find the intersection node of two lists (pointer switching).

Common wrong answers
--------------------
- Storing values instead of nodes in the seen set.
- Reading `fast.next.next` without first checking `fast` and `fast.next`.
- Returning the meeting point instead of the entry.
"""
from __future__ import annotations


class ListNode:
    def __init__(self, val: int = 0, next: ListNode | None = None) -> None:
        self.val = val
        self.next = next


def build(values: list[int], pos: int = -1) -> ListNode | None:
    """Build a list whose tail links back to index `pos` (-1: no cycle)."""
    nodes = [ListNode(v) for v in values]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    if nodes and pos >= 0:
        nodes[-1].next = nodes[pos]
    return nodes[0] if nodes else None


def entry_index(head: ListNode | None, node: ListNode | None) -> int:
    """Index of `node` counting from head (-1 if node is None)."""
    i = 0
    while node is not None:
        if head is node:
            return i
        head, i = head.next, i + 1
    return -1


def brute_force(head: ListNode | None) -> ListNode | None:
    """Hash set of visited nodes (identity, not value)."""
    seen = set()
    while head:
        if head in seen:          # ListNode hashes by identity
            return head
        seen.add(head)
        head = head.next
    return None


def solve(head: ListNode | None) -> ListNode | None:
    """Floyd: meet inside the loop, then walk from head and meeting point together."""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            p = head
            while p is not slow:
                p, slow = p.next, slow.next
            return p
    return None


# Minimal interview version
def interview_version(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            while head is not slow:
                head, slow = head.next, slow.next
            return head
    return None


def main() -> None:
    cases = [([3, 2, 0, -4], 1), ([1, 2], 0), ([1], 0), ([1], -1), ([], -1), ([5, 5, 5, 5], 2)]
    for values, pos in cases:
        head = build(values, pos)
        print(f"values={values} pos={pos} -> entry index {entry_index(head, solve(head))}")


if __name__ == "__main__":
    main()
