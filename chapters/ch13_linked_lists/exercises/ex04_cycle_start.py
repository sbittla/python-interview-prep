"""
Exercise 04 — Where Does the Cycle Begin? (Floyd, phase 2)        [Tier: ★ Core]
Chapter 13 · Pattern: fast/slow pointers · Target time: 20 min

Problem
-------
A singly linked list may end in a loop: the tail's `next` points back to some
earlier node. Return the first node of the loop (the node reached twice when
walking from head), or None if the list ends in None. Do not modify the list.
Also write cycle_length(head): the number of nodes in the loop (0 if none).

Examples
--------
>>> head = build_with_cycle([3, 2, 0, -4], pos=1)   # tail -> node at index 1
>>> solve(head).val
2
>>> solve(build_with_cycle([1, 2], pos=-1)) is None
True

Constraints
-----------
- 0 <= n <= 10**5. Values may repeat, so compare NODES (identity), not values.

Hints
-----
- Phase 1: slow +1, fast +2. If they meet, there is a cycle.
- Phase 2: put one pointer back at head; move both +1. They meet at the entry.
- Why? Let a = head->entry, b = entry->meeting point, c = cycle length.
  At the meeting, fast has walked twice as far: 2(a+b) = a+b+kc, so a = kc - b.
  Walking a steps from the meeting point lands exactly on the entry.

Edge cases
----------
- Empty list; single node with no cycle; single node pointing to itself; cycle
  that starts at head; cycle that is just the tail (tail.next = tail).

Wrong-but-tempting
------------------
- Storing node VALUES in the set: duplicate values give a false cycle.
- Starting phase 2 from the meeting point and from head.next (off by one).
- `while fast.next.next` without checking `fast` / `fast.next` first: AttributeError
  on acyclic lists.

Follow-ups
----------
- Find the duplicate in an array of n+1 values in 1..n by treating i -> nums[i] as
  a linked list (same algorithm, O(1) space, array unmodified).
"""
from __future__ import annotations

from listnode import ListNode, nodes


def build_with_cycle(values: list[int], pos: int = -1) -> ListNode | None:
    """Build a list whose tail points to the node at index `pos` (-1: no cycle)."""
    all_nodes = [ListNode(v) for v in values]
    for a, b in zip(all_nodes, all_nodes[1:]):
        a.next = b
    if all_nodes and pos >= 0:
        all_nodes[-1].next = all_nodes[pos]
    return all_nodes[0] if all_nodes else None


def brute_force(head: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def solve(head: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def cycle_length(head: ListNode | None) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [([3, 2, 0, -4], 1), ([1, 2], 0), ([1], 0), ([1], -1),
             ([], -1), ([5, 5, 5, 5, 5], 3), (list(range(10)), 9)]
    for vals, pos in cases:
        head = build_with_cycle(vals, pos)
        entry = solve(head)
        idx = None
        if entry is not None:
            walk = head
            idx = 0
            while walk is not entry:
                walk, idx = walk.next, idx + 1
        agree = entry is brute_force(head)
        print(f"{vals!s:<32} pos={pos:<2} -> entry index {idx}, "
              f"loop length {cycle_length(head)}, brute agrees {agree}")
    print("acyclic nodes walked:", len(nodes(build_with_cycle([1, 2, 3]))))


if __name__ == "__main__":
    main()
