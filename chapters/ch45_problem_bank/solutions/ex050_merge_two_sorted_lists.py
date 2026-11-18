"""
Exercise 050 — Merge Two Sorted Linked Lists                [Tier: ★ Core]
Chapter 45 · Linked lists · Beginner · Pattern: Dummy head + two pointers · Target time: 10 min

Problem
-------
Two singly linked lists are each sorted in non-decreasing order. Splice their nodes
together into one sorted list and return its head. Reuse the existing nodes; when
values tie, take the node from the first list first (a stable merge).
(Resembles "Merge Two Sorted Lists".)

Examples
--------
>>> to_list(solve(build([1, 3, 5]), build([2, 3, 6])))
[1, 2, 3, 3, 5, 6]
>>> to_list(solve(build([]), build([0])))
[0]
>>> to_list(solve(build([]), build([])))
[]

Constraints
-----------
- 0 <= length of each list <= 10^4
- Both inputs are sorted in non-decreasing order.
- Values may be negative and may repeat.

Hidden edge cases
-----------------
- One or both lists empty.
- One list entirely smaller than the other (the loop ends early; attach the rest).
- Duplicate values across the two lists (stability matters when nodes carry records).

Hints
-----
1. A placeholder "dummy" node in front of the answer removes the special case for the
   first node.
2. When one list runs out, the remainder of the other is already sorted.

Approach ladder
---------------
1. Brute force — pour all values into a Python list, sort, rebuild. O((n+m) log(n+m))
   time, O(n+m) space, new nodes.
2. Optimal — walk both lists with a tail pointer behind a dummy head, always attaching
   the smaller front node. O(n+m) time, O(1) space. We move up because the inputs are
   already sorted, so sorting again wastes the log factor.

Complexity
----------
Optimal: O(n + m) time, O(1) extra space.

Follow-ups
----------
- Merge k sorted lists (see ex094: heap of fronts, O(N log k)).
- Write the recursive merge and explain why its depth is O(n + m).
- Merge two sorted arrays where the first has spare capacity at the end (fill from the back).

Common wrong answers
--------------------
- Using `<` instead of `<=` when comparing, which breaks stability on ties.
- Forgetting to attach the leftover tail, silently dropping elements.
- Returning `dummy` instead of `dummy.next`.
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


def brute_force(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    """Collect, sort, rebuild."""
    return build(sorted(to_list(a) + to_list(b)))


def solve(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    """Dummy head; attach the smaller front node each step."""
    dummy = ListNode()
    tail = dummy
    while a and b:
        if a.val <= b.val:          # <= keeps the merge stable
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a if a else b       # attach whatever is left
    return dummy.next


# Minimal interview version
def interview_version(a, b):
    dummy = tail = ListNode()
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next


def main() -> None:
    cases = [([1, 3, 5], [2, 3, 6]), ([], [0]), ([], []), ([1, 2], [10, 20, 30]), ([-3, 0], [-5, 0])]
    for a, b in cases:
        print(f"merge {a} + {b} -> {to_list(solve(build(a), build(b)))}")
    print(f"interview version: {to_list(interview_version(build([1, 4]), build([2, 3])))}")


if __name__ == "__main__":
    main()
