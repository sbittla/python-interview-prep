"""
Exercise 08 — Construct a Tree from Preorder + Inorder            [Tier: ◆ Extended]
Chapter 14 · Pattern: divide and conquer with an index map · Target time: 25 min

Problem
-------
Given the preorder and inorder traversals of a binary tree with DISTINCT values,
rebuild the tree and return its root. Also rebuild from postorder + inorder.

Examples
--------
>>> to_level(build_pre_in([3, 9, 20, 15, 7], [9, 3, 15, 20, 7]))
[3, 9, 20, None, None, 15, 7]
>>> to_level(build_post_in([9, 15, 7, 20, 3], [9, 3, 15, 20, 7]))
[3, 9, 20, None, None, 15, 7]

Constraints
-----------
- 0 <= n <= 3000; values distinct; both lists describe the same tree.
- The recursive builders need tree height <= ~900 (CPython's 1,000-frame
  limit); build_pre_in_iterative handles any shape, e.g. a 3000-node chain.

Approach ladder
---------------
1. Slicing — preorder[0] is the root; find it in inorder with .index(); everything
   left of it is the left subtree (size k), so recurse on preorder[1:k+1] /
   inorder[:k] and preorder[k+1:] / inorder[k+1:]. O(n^2) time on a chain
   (linear search + slice copies at every level), O(n^2) memory in slices.
2. Index map + bounds (optimal) — a dict value -> inorder position makes the
   lookup O(1); pass (lo, hi) bounds into inorder instead of slicing, and consume
   preorder left to right with a shared iterator (roots appear in exactly the
   order we create nodes). O(n) time, O(n) space, O(h) recursion.
3. Postorder variant — roots come from the END of postorder, so build the RIGHT
   subtree before the left.
4. Explicit stack (any depth) — keep the current root-to-node path on a stack;
   each new preorder value is the left child of the top, unless the top equals
   the next unclosed inorder value: then pop while it does, and the new value is
   the right child of the last node popped. O(n) time, O(h) stack.

Hints
-----
- Why distinct values? With duplicates the root's inorder position is ambiguous:
  [1, 1] / [1, 1] fits two different trees.
- Preorder + postorder alone does not determine a tree (a lone child could be
  left or right) unless every node has 0 or 2 children.

Edge cases
----------
- Empty lists -> None; single node; left-only and right-only chains.

Wrong-but-tempting
------------------
- Building left from preorder[1:k] (off by one): k = size of the left subtree, so
  the left part is preorder[1:k + 1].
- Postorder version building left first: consumes right-subtree roots as left ones.

Follow-ups
----------
- Build a BST from its preorder alone: O(n) with an upper bound passed down.
- Verify that the two lists are consistent (raise ValueError otherwise).
"""
from __future__ import annotations

from treenode import TreeNode, render, to_level


def build_slicing(preorder: list[int], inorder: list[int]) -> TreeNode | None:
    if not preorder:
        return None
    root = TreeNode(preorder[0])
    k = inorder.index(root.val)                # size of the left subtree
    root.left = build_slicing(preorder[1:k + 1], inorder[:k])
    root.right = build_slicing(preorder[k + 1:], inorder[k + 1:])
    return root


def build_pre_in(preorder: list[int], inorder: list[int]) -> TreeNode | None:
    where = {v: i for i, v in enumerate(inorder)}
    roots = iter(preorder)                     # next root, in creation order

    def make(lo: int, hi: int) -> TreeNode | None:   # inorder[lo:hi]
        if lo == hi:
            return None
        node = TreeNode(next(roots))
        mid = where[node.val]
        node.left = make(lo, mid)              # left first: preorder order
        node.right = make(mid + 1, hi)
        return node

    return make(0, len(inorder))


def build_pre_in_iterative(preorder: list[int], inorder: list[int]) -> TreeNode | None:
    if not preorder:
        return None
    root = TreeNode(preorder[0])
    stack, i = [root], 0                       # inorder[i]: next node to "close"
    for v in preorder[1:]:
        node, parent = TreeNode(v), None
        while stack and stack[-1].val == inorder[i]:
            parent = stack.pop()               # its left side is finished
            i += 1
        if parent:
            parent.right = node
        else:
            stack[-1].left = node
        stack.append(node)
    return root


def build_post_in(postorder: list[int], inorder: list[int]) -> TreeNode | None:
    where = {v: i for i, v in enumerate(inorder)}
    roots = iter(reversed(postorder))          # root, right..., left...

    def make(lo: int, hi: int) -> TreeNode | None:
        if lo == hi:
            return None
        node = TreeNode(next(roots))
        mid = where[node.val]
        node.right = make(mid + 1, hi)         # right first!
        node.left = make(lo, mid)
        return node

    return make(0, len(inorder))


def main() -> None:
    pre, ino, post = [3, 9, 20, 15, 7], [9, 3, 15, 20, 7], [9, 15, 7, 20, 3]
    root = build_pre_in(pre, ino)
    print(render(root))
    print("pre+in :", to_level(root))
    print("slicing:", to_level(build_slicing(pre, ino)))
    print("post+in:", to_level(build_post_in(post, ino)))
    print("left chain :", to_level(build_pre_in([1, 2, 3], [3, 2, 1])))
    print("right chain:", to_level(build_pre_in([1, 2, 3], [1, 2, 3])))
    print("empty      :", to_level(build_pre_in([], [])))
    print("iterative  :", to_level(build_pre_in_iterative(pre, ino)))
    n = 3000                                   # a left chain: too deep to recurse
    deep = build_pre_in_iterative(list(range(n)), list(range(n - 1, -1, -1)))
    depth = 0
    while deep:
        depth, deep = depth + 1, deep.left
    print("3000-node left chain, iterative build, depth:", depth)


if __name__ == "__main__":
    main()
