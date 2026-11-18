"""
Exercise 055 — Deep-Copy a List With Random Pointers                [Tier: ◆ Extended]
Chapter 45 · Linked lists · Intermediate · Pattern: Hash map old->new / node interleaving · Target time: 20 min

Problem
-------
Each node in a singly linked list has `val`, `next`, and an extra `random` pointer
that refers to any node in the list or to None. Produce a deep copy: brand-new
nodes whose `next` and `random` pointers mirror the original structure, with no
pointer into the original list. The original must be left unchanged.
(Resembles "Copy List with Random Pointer".)

Examples
--------
Lists are described as [(val, random_index), ...]; `describe` turns a list back into
that form so copies can be compared.

>>> describe(solve(build([(7, None), (13, 0), (11, 4), (10, 2), (1, 0)])))
[(7, None), (13, 0), (11, 4), (10, 2), (1, 0)]
>>> describe(solve(build([(1, 0)])))
[(1, 0)]
>>> solve(None) is None
True

Constraints
-----------
- 0 <= number of nodes <= 1000
- Values may repeat; identity, not value, defines structure.

Hidden edge cases
-----------------
- Random pointing to the node itself.
- Random pointers that point forward (to nodes not yet copied).
- Duplicate values — mapping by value breaks.
- Restoring the original list in the interleaving approach.

Hints
-----
1. The difficulty is a `random` pointer to a node you have not copied yet. What if you
   created all copies first?
2. For O(1) extra space: put each copy right after its original (A -> A' -> B -> B').
   Then `A'.random` is `A.random.next`.

Approach ladder
---------------
1. Brute force — two passes with a dict {original: copy}: create all copies, then wire
   `next` and `random` through the dict. O(n) time, O(n) extra space.
2. Optimal (space) — interleave copies into the original list, set randoms via
   `orig.random.next`, then unzip the two lists. O(n) time, O(1) extra space beyond the
   output. Move up only if asked for O(1) space; the dict version is the cleaner default.

Complexity
----------
Hash map: O(n) time, O(n) extra. Interleaving: O(n) time, O(1) extra.

Follow-ups
----------
- Clone a general graph (see ex083) — same dict idea with BFS/DFS.
- Clone a binary tree with random pointers.
- Why does `copy.deepcopy` work here, and why is it not an acceptable interview answer?

Common wrong answers
--------------------
- Keying the map by value instead of by node.
- Leaving the original list interleaved (mutated) after the interleaving approach.
- Copying `random` pointers that still point into the original list (shallow copy).
"""
from __future__ import annotations


class Node:
    def __init__(self, val: int, next: Node | None = None, random: Node | None = None) -> None:
        self.val = val
        self.next = next
        self.random = random


def build(spec: list[tuple[int, int | None]]) -> Node | None:
    nodes = [Node(v) for v, _ in spec]
    for i, (_, r) in enumerate(spec):
        if i + 1 < len(nodes):
            nodes[i].next = nodes[i + 1]
        nodes[i].random = nodes[r] if r is not None else None
    return nodes[0] if nodes else None


def describe(head: Node | None) -> list[tuple[int, int | None]]:
    nodes = []
    while head:
        nodes.append(head)
        head = head.next
    index = {node: i for i, node in enumerate(nodes)}
    return [(n.val, index[n.random] if n.random else None) for n in nodes]


def brute_force(head: Node | None) -> Node | None:
    """Dict from original node to its copy."""
    copy = {None: None}
    node = head
    while node:
        copy[node] = Node(node.val)
        node = node.next
    node = head
    while node:
        copy[node].next = copy[node.next]
        copy[node].random = copy[node.random]
        node = node.next
    return copy[head]


def solve(head: Node | None) -> Node | None:
    """Interleave copies (A -> A' -> B -> B'), set randoms, unzip. O(1) extra space."""
    if head is None:
        return None
    node = head
    while node:                                   # 1. weave copies in
        node.next = Node(node.val, node.next)
        node = node.next.next
    node = head
    while node:                                   # 2. randoms
        node.next.random = node.random.next if node.random else None
        node = node.next.next
    new_head = head.next
    node = head
    while node:                                   # 3. unzip, restoring the original
        clone = node.next
        node.next = clone.next
        clone.next = clone.next.next if clone.next else None
        node = node.next
    return new_head


# Minimal interview version (dict, the one to write first)
def interview_version(head):
    m = {None: None}
    n = head
    while n:
        m[n] = Node(n.val)
        n = n.next
    for old, new in m.items():
        if old:
            new.next, new.random = m[old.next], m[old.random]
    return m[head]


def main() -> None:
    specs = [
        [(7, None), (13, 0), (11, 4), (10, 2), (1, 0)],
        [(1, 1), (2, 1)],
        [(3, None), (3, 0), (3, None)],
        [(1, 0)],
        [],
    ]
    for spec in specs:
        original = build(spec)
        clone = solve(original)
        shares = False
        a, b = original, clone
        while a:
            shares = shares or a is b
            a, b = a.next, b.next
        print(f"{spec} -> copy {describe(clone)} | original intact: "
              f"{describe(original) == spec} | shares nodes: {shares}")


if __name__ == "__main__":
    main()
