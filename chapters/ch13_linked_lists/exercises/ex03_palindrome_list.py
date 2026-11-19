"""
Exercise 03 — Middle Node and Palindrome List (restore the list)   [Tier: ★ Core]
Chapter 13 · Pattern: fast/slow pointers + in-place reversal · Target time: 20 min

Problem
-------
1. middle(head): return the middle node; for an even length return the SECOND of
   the two middle nodes. Return None for an empty list.
2. is_palindrome(head): return True if the values read the same forwards and
   backwards. Use O(1) extra space, and leave the list exactly as you found it
   (same nodes, same order) when you return — callers may still be using it.

Examples
--------
>>> middle(build([1, 2, 3, 4, 5])).val, middle(build([1, 2, 3, 4])).val
(3, 3)
>>> is_palindrome(build([1, 2, 2, 1])), is_palindrome(build([1, 2, 3]))
(True, False)

Constraints
-----------
- 0 <= n <= 10**5.

Hints
-----
- slow moves 1, fast moves 2. When fast falls off the end, slow is in the middle.
  The loop condition decides which middle you get.
- Reverse the second half, compare it with the first half, then reverse it back.

Edge cases
----------
- Empty and single-node lists (palindromes); even and odd lengths; [1, 2] (False).

Wrong-but-tempting
------------------
- Not restoring the list: the caller's list is silently cut in half.
- `while fast.next and fast.next.next` gives the FIRST middle on even lengths —
  fine for palindrome, wrong for the stated middle() contract.

Follow-ups
----------
- Reorder L0, Ln, L1, Ln-1, ... (same three steps; see chapters/ch45_problem_bank).
- Delete the middle node.
"""
from __future__ import annotations

from listnode import ListNode, build, nodes, to_list


def middle(head: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def _reverse(head: ListNode | None) -> ListNode | None:
    raise NotImplementedError("TODO")


def brute_force(head: ListNode | None) -> bool:
    raise NotImplementedError("TODO")


def is_palindrome(head: ListNode | None) -> bool:
    raise NotImplementedError("TODO")


def main() -> None:
    for vals in ([1, 2, 3, 4, 5], [1, 2, 3, 4], [1], []):
        m = middle(build(vals))
        print(f"middle of {vals!s:<16} -> {m.val if m else None}")
    for vals in ([1, 2, 2, 1], [1, 2, 3, 2, 1], [1, 2], [1, 2, 3], [], [9]):
        head = build(vals)
        before = nodes(head)
        res = is_palindrome(head)
        print(f"palindrome {vals!s:<16} -> {res!s:<5} restored={nodes(head) == before}")


if __name__ == "__main__":
    main()
