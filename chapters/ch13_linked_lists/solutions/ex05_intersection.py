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

Approach ladder
---------------
1. Brute force — for every node of a, scan all of b. O(m*n) time, O(1) space.
2. Improved   — put every node of a in a set (by identity); first node of b in the
   set wins. O(m+n) time, O(m) space.
3. Optimal    — measure both lengths, advance the longer by the difference, walk in
   lockstep; or the "switch heads" trick. O(m+n) time, O(1) space.

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
    while a is not None:
        cur = b
        while cur is not None:
            if cur is a:
                return a
            cur = cur.next
        a = a.next
    return None


def with_set(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    seen = set()
    while a is not None:
        seen.add(id(a))
        a = a.next
    while b is not None:
        if id(b) in seen:
            return b
        b = b.next
    return None


def solve(a: ListNode | None, b: ListNode | None) -> ListNode | None:
    p, q = a, b
    while p is not q:                     # both None after len(a)+len(b) steps at most
        p = p.next if p is not None else b
        q = q.next if q is not None else a
    return p


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
