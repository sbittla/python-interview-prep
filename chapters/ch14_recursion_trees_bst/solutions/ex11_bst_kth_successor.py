"""
Exercise 11 — Kth Smallest and Inorder Successor in a BST         [Tier: ★ Core]
Chapter 14 · Pattern: inorder = sorted order; BST descent · Target time: 20 min

Problem
-------
For a BST with distinct keys:
(a) kth_smallest(root, k): the k-th smallest key (1-indexed), 1 <= k <= n;
(b) successor(root, x): the smallest key strictly greater than x, or None.
    x need not be in the tree. No parent pointers.

Examples
--------
>>> root = build([5, 3, 6, 2, 4, None, None, 1])
>>> kth_smallest(root, 3)
3
>>> successor(root, 4), successor(root, 6), successor(root, 0)
(5, None, 1)

Constraints
-----------
- 1 <= n <= 10**4.

Approach ladder
---------------
(a) 1. Full inorder into a list, return item k-1: O(n) time and space.
    2. Iterative inorder that STOPS after k pops: O(h + k) time, O(h) space.
    3. Many queries with inserts/deletes in between: store subtree sizes in each
       node, then descend: O(h) per query (order-statistic tree).
(b) 1. Full inorder, then bisect for the first key > x: O(n).
    2. Descend from the root: whenever node.val > x, it is a candidate — record
       it and go LEFT for a smaller one; otherwise go right. O(h) time, O(1) space.
       (If the node has a right subtree, this walk ends at that subtree's
       leftmost node; if not, at the lowest ancestor we went left from.)

Hints
-----
- (a) Reuse the "go left, pop, turn right" loop from ex03 with a counter.
- (b) It is the BST version of "first element > x", i.e. upper bound (→ §11.2).

Edge cases
----------
- k = 1 (minimum), k = n (maximum); x below the minimum, x >= the maximum,
  x between two keys.

Wrong-but-tempting
------------------
- (b) "Successor = leftmost node of x's right subtree" only: wrong when x has no
  right subtree (the answer is an ancestor).
- (a) Recursive inorder with a global counter that isn't reset between calls.

Follow-ups
----------
- Predecessor: mirror image (node.val < x -> candidate, go right).
- BST iterator with next()/has_next() in O(h) memory: keep the inorder stack.
"""
from __future__ import annotations

from bisect import bisect_right

from treenode import TreeNode, build, inorder_values, render


def kth_smallest_brute(root: TreeNode | None, k: int) -> int:
    return inorder_values(root)[k - 1]


def kth_smallest(root: TreeNode | None, k: int) -> int:
    stack: list[TreeNode] = []
    node = root
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.val                    # stop early: O(h + k)
        node = node.right
    raise ValueError("k is larger than the tree")


def successor_brute(root: TreeNode | None, x: int) -> int | None:
    vals = inorder_values(root)
    i = bisect_right(vals, x)
    return vals[i] if i < len(vals) else None


def successor(root: TreeNode | None, x: int) -> int | None:
    best = None
    node = root
    while node:
        if node.val > x:
            best = node.val                    # candidate; look for a smaller one
            node = node.left
        else:
            node = node.right
    return best


def main() -> None:
    root = build([5, 3, 6, 2, 4, None, None, 1])
    print(render(root))
    print("kth  :", [kth_smallest(root, k) for k in range(1, 7)],
          "brute:", [kth_smallest_brute(root, k) for k in range(1, 7)])
    for x in (0, 1, 4, 5, 6, 10, 3):
        print(f"successor({x:>2}) = {successor(root, x)!s:<4} brute = {successor_brute(root, x)}")


if __name__ == "__main__":
    main()
