"""
Exercise 15 — Recursion That Hits the Limit             [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (recursion) · Target time: 8 min

Problem
-------
`chain_length(node)` returns the number of nodes in a singly linked list. The
buggy version is the textbook recursion `1 + chain_length(node.next)`; on a list
of 10,000 nodes it raises `RecursionError`, because CPython's default recursion
limit is about 1000 frames and Python performs no tail-call optimisation.

Examples
--------
>>> chain_length(build_chain(3))
3
>>> chain_length(build_chain(10_000))
10000

Constraints
-----------
- Up to 10**6 nodes.

Approach ladder
---------------
1. Buggy  — recursion depth = list length: O(n) stack frames.
2. Patch  — `sys.setrecursionlimit(20_000)`: works for this input, but the next,
   deeper input fails again, every frame costs memory, and recursion that runs
   through C code can overflow the C stack and crash the process — not a real fix.
3. Fixed  — iterate: a `while` loop walking `node = node.next`. O(n) time, O(1) space.
   For tree DFS, use an explicit stack list.

Follow-ups
----------
- Convert recursive DFS on a deep tree to an explicit stack.
- Why doesn't `return chain_length(node.next, acc + 1)` (tail call) help? (CPython
  never eliminates tail calls; each call still pushes a frame.)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass
class Node:
    value: int
    next: "Node | None" = None


def build_chain(n: int) -> Node | None:
    head = None
    for v in range(n, 0, -1):
        head = Node(v, head)
    return head


def buggy_chain_length(node: Node | None) -> int:
    if node is None:
        return 0
    return 1 + buggy_chain_length(node.next)


def chain_length(node: Node | None) -> int:
    """Iterative walk: O(n) time, O(1) extra space, no depth limit."""
    count = 0
    while node is not None:
        count += 1
        node = node.next
    return count


def main() -> None:
    print("default recursion limit:", sys.getrecursionlimit())
    print("buggy on 500 nodes:", buggy_chain_length(build_chain(500)))
    try:
        buggy_chain_length(build_chain(10_000))
    except RecursionError as exc:
        print("buggy on 10000 nodes:", type(exc).__name__)
    print("fixed on 10000 nodes:", chain_length(build_chain(10_000)))
    print("fixed on empty list:", chain_length(None))


if __name__ == "__main__":
    main()
