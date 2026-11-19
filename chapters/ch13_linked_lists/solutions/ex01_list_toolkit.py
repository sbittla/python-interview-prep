"""
Exercise 01 — Linked-List Toolkit: length, insert, delete, reverse     [Tier: ★ Core]
Chapter 13 · Pattern: pointer walking, dummy head · Target time: 20 min

Problem
-------
Using `ListNode` from `listnode.py`, write the four operations every later exercise
leans on. Positions are 0-based; every function returns the (possibly new) head.

- length(head)               number of nodes.
- insert_at(head, i, val)    insert a new node so it ends up at position i
                             (0 <= i <= length); raise IndexError otherwise.
- delete_at(head, i)         unlink the node at position i (0 <= i < length);
                             raise IndexError otherwise.
- reverse(head)              reverse in place, O(1) extra space.
- reverse_recursive(head)    same result, written recursively (O(n) call stack).

Examples
--------
>>> to_list(insert_at(build([1, 3]), 1, 2))
[1, 2, 3]
>>> to_list(delete_at(build([1, 2, 3]), 0))
[2, 3]
>>> to_list(reverse(build([1, 2, 3])))
[3, 2, 1]

Constraints
-----------
- 0 <= n <= 10**5. Values are ints.

Hints
-----
- A dummy node in front of head makes "insert/delete at position 0" the same code
  path as every other position.
- To reverse, keep three names: prev, cur, nxt. Save cur.next BEFORE overwriting it.
- Recursive reverse: reverse the rest, then make head.next point back at head and
  set head.next = None (forgetting that line leaves a 2-node cycle).

Approach ladder
---------------
1. Brute force — copy values to a Python list, edit it, rebuild. O(n) time and O(n)
   space, and it allocates new nodes, so callers holding node references break.
2. Improved   — walk to position i-1 and relink; special-case i == 0. O(i) time.
3. Optimal    — same walk but from a dummy node: no special case. O(i) time, O(1)
   space. Reverse iteratively (O(1) space) rather than recursively (O(n) stack;
   RecursionError past ~1,000 nodes in CPython by default).

Edge cases
----------
- Empty list; i == length (append); i out of range (negative or too large);
  single node reversal; 10**5-node reversal.

Follow-ups
----------
- Reverse only positions left..right in one pass.
- Insert into a sorted list (walk while next.val < val).
"""
from __future__ import annotations

import sys

from listnode import ListNode, build, render, to_list


def length(head: ListNode | None) -> int:
    n = 0
    while head is not None:
        n, head = n + 1, head.next
    return n


def brute_force_insert(head: ListNode | None, i: int, val: int) -> ListNode | None:
    vals = to_list(head)
    if not 0 <= i <= len(vals):
        raise IndexError(i)
    vals.insert(i, val)
    return build(vals)


def insert_at(head: ListNode | None, i: int, val: int) -> ListNode | None:
    if i < 0:
        raise IndexError(i)
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(i):                    # stop at the node BEFORE position i
        prev = prev.next
        if prev is None:
            raise IndexError(i)
    prev.next = ListNode(val, prev.next)
    return dummy.next


def delete_at(head: ListNode | None, i: int) -> ListNode | None:
    if i < 0:
        raise IndexError(i)
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(i):
        prev = prev.next
        if prev is None:
            raise IndexError(i)
    if prev.next is None:
        raise IndexError(i)
    prev.next = prev.next.next            # unlink; the old node is garbage-collected
    return dummy.next


def reverse(head: ListNode | None) -> ListNode | None:
    prev, cur = None, head
    while cur:
        nxt = cur.next      # 1. save the rest of the list
        cur.next = prev     # 2. flip this arrow
        prev = cur          # 3. advance prev
        cur = nxt           # 4. advance cur
    return prev             # cur is None; prev is the old tail


def reverse_recursive(head: ListNode | None) -> ListNode | None:
    if head is None or head.next is None:
        return head
    new_head = reverse_recursive(head.next)
    head.next.next = head   # the old successor now points back at us
    head.next = None        # we are the new tail
    return new_head


def main() -> None:
    head = build([10, 20, 30])
    print("start          :", render(head), "length", length(head))
    head = insert_at(head, 0, 5)
    print("insert_at(0,5) :", render(head))
    head = insert_at(head, 4, 40)
    print("insert_at(4,40):", render(head))
    head = delete_at(head, 2)
    print("delete_at(2)   :", render(head))
    print("reverse        :", render(reverse(head)))
    print("recursive      :", render(reverse_recursive(build([1, 2, 3]))))
    print("reverse []     :", render(reverse(None)))
    try:
        delete_at(build([1]), 1)
    except IndexError as e:
        print("delete_at([1], 1) -> IndexError", e)
    big = build(range(100_000))
    print("iterative 100000 nodes, new head:", reverse(big).val)
    print("recursion limit:", sys.getrecursionlimit())
    try:
        reverse_recursive(build(range(5_000)))
    except RecursionError:
        print("recursive 5000 nodes -> RecursionError")


if __name__ == "__main__":
    main()
