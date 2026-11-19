"""
Exercise 07 — Lowest Common Ancestor: Binary Tree and BST          [Tier: ★ Core]
Chapter 14 · Pattern: return info up the tree; BST ordering · Target time: 20 min

Problem
-------
Given the root and two nodes p and q that are both in the tree, return their
lowest common ancestor: the deepest node that has both p and q as descendants
(a node is a descendant of itself).
(a) lca(root, p, q) for any binary tree;
(b) lca_bst(root, p, q) for a binary search tree with distinct keys, in O(h)
    time and O(1) extra space.

Examples
--------
>>> t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
>>> lca(t, find(t, 5), find(t, 4)).val
5
>>> b = build([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
>>> lca_bst(b, find(b, 2), find(b, 8)).val
6

Constraints
-----------
- 2 <= n <= 10**5; p is not q; both are present. Compare nodes by identity.

Approach ladder
---------------
1. Parent pointers — one traversal builds a parent dict; collect p's ancestors in
   a set, then walk up from q until you hit one. O(n) time, O(n) space; iterative,
   so any depth works.
2. Return info up the tree — recurse into both children. If both sides report a
   match, this node is the LCA; otherwise pass up whichever side is non-None (or
   the node itself if it is p or q). O(n) time, O(h) stack, no extra dict.
3. BST — keys tell you which side to go: both smaller -> go left, both larger ->
   go right, otherwise (split or equal) the current node is the LCA.
   O(h) time, O(1) space.

Hints
-----
- (a) Base case: `if node is None or node is p or node is q: return node`.
- (b) A loop, not recursion: nothing needs to come back up.

Edge cases
----------
- p is an ancestor of q (answer p); p and q are siblings; one of them is the root.

Wrong-but-tempting
------------------
- (a) Comparing values instead of nodes when values repeat.
- (a) Returning early when p is found and assuming q is below it: correct only
  because the prompt promises both exist (see follow-up).
- (b) Using the general O(n) algorithm on a BST: correct but ignores the hint the
  interviewer gave you.

Follow-ups
----------
- q may be absent: count how many of p, q were actually found; return None unless 2.
- Many queries on one tree: binary lifting / Euler tour + RMQ (O(log n) per query).
"""
from __future__ import annotations

from treenode import TreeNode, build, render


def find(root: TreeNode | None, val: int) -> TreeNode | None:
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        if node.val == val:
            return node
        stack += [c for c in (node.left, node.right) if c]
    return None


def lca_parent_map(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    parent: dict[int, TreeNode | None] = {id(root): None}
    stack = [root]
    while stack:
        node = stack.pop()
        for c in (node.left, node.right):
            if c:
                parent[id(c)] = node
                stack.append(c)
    ancestors = set()
    node: TreeNode | None = p
    while node:
        ancestors.add(id(node))
        node = parent[id(node)]
    node = q
    while id(node) not in ancestors:
        node = parent[id(node)]
    return node


def lca(root: TreeNode | None, p: TreeNode, q: TreeNode) -> TreeNode | None:
    if root is None or root is p or root is q:
        return root
    left = lca(root.left, p, q)
    right = lca(root.right, p, q)
    if left and right:
        return root                     # p and q on different sides
    return left or right                # pass up whatever was found


def lca_bst(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    node = root
    while True:
        if p.val < node.val and q.val < node.val:
            node = node.left
        elif p.val > node.val and q.val > node.val:
            node = node.right
        else:
            return node                 # split point (or equal to p or q)


def main() -> None:
    t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    print(render(t))
    for a, b in [(5, 1), (5, 4), (6, 4), (7, 8), (3, 0)]:
        p, q = find(t, a), find(t, b)
        print(f"lca({a}, {b}) = {lca(t, p, q).val}  parent-map = {lca_parent_map(t, p, q).val}")
    bst = build([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
    print(render(bst))
    for a, b in [(2, 8), (2, 4), (3, 5), (0, 5), (7, 9)]:
        print(f"lca_bst({a}, {b}) = {lca_bst(bst, find(bst, a), find(bst, b)).val}")


if __name__ == "__main__":
    main()
