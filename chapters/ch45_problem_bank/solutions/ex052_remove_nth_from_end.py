"""
Exercise 052 — Remove the k-th Node From the End                [Tier: ★ Core]
Chapter 45 · Linked lists · Intermediate · Pattern: Two pointers with a fixed gap · Target time: 12 min

Problem
-------
Given the head of a singly linked list and an integer k (1-indexed, counted from the
tail), unlink the k-th node from the end and return the head of the resulting list.
Aim for a single pass. (Resembles "Remove Nth Node From End of List".)

Examples
--------
>>> to_list(solve(build([1, 2, 3, 4, 5]), 2))
[1, 2, 3, 5]
>>> to_list(solve(build([1]), 1))
[]
>>> to_list(solve(build([1, 2]), 2))
[2]

Constraints
-----------
- 1 <= number of nodes <= 10^5
- 1 <= k <= number of nodes

Hidden edge cases
-----------------
- Removing the head (k equals the length) — the head pointer itself changes.
- A one-node list becomes empty.
- Removing the last node (k = 1).

Hints
-----
1. If one pointer starts k steps ahead of another and both move together, where is the
   trailing pointer when the leader falls off the end?
2. A dummy node before the head makes "remove the head" an ordinary case.

Approach ladder
---------------
1. Brute force — first pass counts the length n; second pass stops at node n - k and
   unlinks its successor. O(n) time, O(1) space, two passes.
2. Optimal — dummy head; advance `lead` k + 1 steps, then move `lead` and `trail`
   together until `lead` is None; `trail.next` is the victim. O(n) time, O(1) space,
   one pass. We move up because the interviewer usually asks for one pass and the gap
   technique generalises (middle node, k-th from end).

Complexity
----------
Optimal: O(n) time, O(1) extra space, one pass.

Follow-ups
----------
- Return the k-th node from the end without removing it.
- What if k may exceed the length? Return the list unchanged and say so.
- Remove every node whose value equals a target (dummy head again).

Common wrong answers
--------------------
- Starting both pointers at the head without a dummy, then crashing when k == length.
- Off-by-one: advancing the leader k steps instead of k + 1 from the dummy.
- Returning the original `head` after the head was removed.
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
    """Two passes: count, then walk to the predecessor."""
    n = 0
    node = head
    while node:
        n, node = n + 1, node.next
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(n - k):
        prev = prev.next
    prev.next = prev.next.next
    return dummy.next


def solve(head: ListNode | None, k: int) -> ListNode | None:
    """One pass: keep a gap of k nodes between lead and trail."""
    dummy = ListNode(0, head)
    lead = trail = dummy
    for _ in range(k + 1):          # gap of k nodes between trail and lead
        lead = lead.next
    while lead:
        lead, trail = lead.next, trail.next
    trail.next = trail.next.next    # trail is the predecessor of the victim
    return dummy.next


# Minimal interview version
def interview_version(head, k):
    dummy = trail = ListNode(0, head)
    lead = head
    for _ in range(k):
        lead = lead.next
    while lead:
        lead, trail = lead.next, trail.next
    trail.next = trail.next.next
    return dummy.next


def main() -> None:
    for values, k in [([1, 2, 3, 4, 5], 2), ([1], 1), ([1, 2], 2), ([1, 2], 1), ([9, 8, 7], 3)]:
        print(f"remove {k}-th from end of {values} -> {to_list(solve(build(values), k))}")


if __name__ == "__main__":
    main()
