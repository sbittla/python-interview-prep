"""
Exercise 05 — Intersection of Two Lists                         [Tier: ★ Core]
Chapter 13 · Pattern: two pointers, length alignment · Target time: 15 min

Problem
-------
Two acyclic singly linked lists may merge: from some node onward they share the
same node objects (a Y shape). Return the first shared node, or None. Equal values
do not count — only the same node object does. Do not modify either list.

Examples
--------
    a: 4 -> 1 ------+
                    v
                    8 -> 4 -> 5 -> None
                    ^
    b: 5 -> 6 -> 1 -+
>>> a, b = build_y([4, 1], [5, 6, 1], [8, 4, 5])
>>> solve(a, b).val
8

Constraints
-----------
- 0 <= len(a), len(b) <= 10**5. Neither list has a cycle.

Hints
-----
- If both lists had the same length, walking in lockstep would meet at the merge.
- Skip the longer list's extra prefix first — or let each pointer, on reaching the
  end, jump to the OTHER list's head. Both then walk len(a) + len(b) steps.

Edge cases
----------
- Either list empty; no intersection (the switch trick ends with both None);
  intersection at the very first node; equal values but distinct nodes.

Follow-ups
----------
- What if the lists may contain cycles? (Find each cycle entry with Floyd first.)
"""
from __future__ import annotations

from listnode import ListNode, build


def build_y(a_only: list[int], b_only: list[int], shared: list[int]):
    """Return heads (a, b) of two lists that share the `shared` tail nodes."""
    tail = build(shared)
    def attach(prefix: list[int]) -> ListNode | None:
        head = build(prefix)
        if head is None:
            return tail
        cur = head
        while cur.next is not None:
            cur = cur.next
        cur.next = tail
        return head
    return attach(a_only), attach(b_only)


def brute_force(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def with_set(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def solve(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [([4, 1], [5, 6, 1], [8, 4, 5]), ([1, 9, 1], [3], [2, 4]),
             ([2, 6, 4], [1, 5], []), ([], [7], [7]), ([], [], [])]
    for a_only, b_only, shared in cases:
        a, b = build_y(a_only, b_only, shared)
        node = solve(a, b)
        same = node is with_set(a, b) and node is brute_force(a, b)
        print(f"a-only={a_only!s:<10} b-only={b_only!s:<10} shared={shared!s:<10}"
              f" -> {node.val if node else None}  all rungs agree {same}")
    x, y = build([1, 2, 3]), build([1, 2, 3])
    print("equal values, distinct nodes ->", solve(x, y))


if __name__ == "__main__":
    main()
