"""
Exercise 049 — Reverse a Singly Linked List                [Tier: ★ Core]
Chapter 45 · Linked lists · Beginner · Pattern: Pointer reversal · Target time: 10 min

Problem
-------
You are given the head of a singly linked list. Rearrange the `next` pointers so the
list runs in the opposite direction and return the new head. Do not create new nodes
in the optimal version. (Resembles the well-known "Reverse Linked List" problem.)

Examples
--------
>>> to_list(solve(build([1, 2, 3, 4])))
[4, 3, 2, 1]
>>> to_list(solve(build([7])))
[7]
>>> to_list(solve(build([])))
[]

Constraints
-----------
- 0 <= number of nodes <= 10^5
- Node values are arbitrary integers.
- O(1) extra space is expected for the optimal answer.

Hidden edge cases
-----------------
- Empty list (head is None) must return None, not crash.
- Single node: its `next` must stay None.
- Long lists (10^5 nodes) break a naive recursive version on CPython's recursion limit.

Hints
-----
1. Walk the list once. At each node you need to remember three things: where you came
   from, where you are, and where you are going next.
2. Save `cur.next` before you overwrite it.

Approach ladder
---------------
1. Brute force — copy the values into a Python list, then build a fresh list in reverse
   order. O(n) time, O(n) extra space, and it allocates new nodes (often disallowed).
2. Recursive — reverse the tail, then hook the current node onto its end. O(n) time
   but O(n) call stack: fails for long lists.
3. Optimal — iterative three-pointer walk (prev, cur, nxt) flipping one arrow per step.
   O(n) time, O(1) space. We move up because it keeps the original nodes and needs
   no stack.

Complexity
----------
Optimal: O(n) time, O(1) extra space.

Follow-ups
----------
- Reverse only positions left..right (1-indexed) in one pass.
- Reverse a doubly linked list (swap prev/next on each node).
- Check whether a list is a palindrome using reversal of the second half.

Common wrong answers
--------------------
- Overwriting `cur.next` before saving it, which loses the rest of the list.
- Returning `head` (now the tail) instead of `prev`.
- Forgetting to set the old head's `next` to None, which creates a two-node cycle.
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


def brute_force(head: ListNode | None) -> ListNode | None:
    """Copy values out, rebuild reversed (allocates new nodes)."""
    return build(to_list(head)[::-1])


def solve(head: ListNode | None) -> ListNode | None:
    """Iterative in-place reversal: flip one arrow per step."""
    prev = None
    cur = head
    while cur:
        nxt = cur.next      # remember the rest of the list
        cur.next = prev     # flip this arrow
        prev = cur          # advance both pointers
        cur = nxt
    return prev


# Minimal interview version
def interview_version(head):
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next
    return prev


def main() -> None:
    for values in ([1, 2, 3, 4], [7], [], [5, 5, 1]):
        print(f"reverse {values} -> {to_list(solve(build(values)))}")
    long_list = build(list(range(100_000)))
    rev = to_list(solve(long_list))
    print(f"100000 nodes: first={rev[0]} last={rev[-1]}")
    print(f"brute force agrees: {to_list(brute_force(build([1, 2, 3]))) == [3, 2, 1]}")
    print(f"interview version: {to_list(interview_version(build([1, 2, 3])))}")


if __name__ == "__main__":
    main()
