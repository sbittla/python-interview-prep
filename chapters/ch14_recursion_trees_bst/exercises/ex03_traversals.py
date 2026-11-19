"""
Exercise 03 — Preorder, Inorder, Postorder: Recursive and Iterative   [Tier: ★ Core]
Chapter 14 · Pattern: DFS with an explicit stack · Target time: 25 min

Problem
-------
Return the values of a binary tree in preorder (node, left, right), inorder
(left, node, right) and postorder (left, right, node). Write each recursively
and iteratively; the iterative versions must handle a 100,000-node chain.

Examples
--------
The tree [1, 2, 3, 4, 5] has root 1, children 2 and 3, and 4, 5 under 2.
>>> root = build([1, 2, 3, 4, 5])
>>> preorder_iterative(root)
[1, 2, 4, 5, 3]
>>> inorder_iterative(root)
[4, 2, 5, 1, 3]
>>> postorder_iterative(root)
[4, 5, 2, 3, 1]

Constraints
-----------
- 0 <= n <= 10**5; the tree may be a single chain (height n).

Hints
-----
- Push order is the reverse of processing order (stack = LIFO).
- Inorder iterative loop condition: `while stack or node`.

Edge cases
----------
- Empty tree; single node; left-only chain; right-only chain.

Wrong-but-tempting
------------------
- Preorder pushing left before right: you get node, right, left.
- Postorder via "reverse of preorder": reverse of (node, left, right) is
  (right, left, node), not postorder. Reverse (node, right, left) instead.

Follow-ups
----------
- O(1) extra space: Morris traversal (temporarily threads right pointers).
- Return an iterator (BST iterator): keep the inorder stack between next() calls.
"""
from __future__ import annotations

from treenode import TreeNode, build, chain, render


def preorder_recursive(root: TreeNode | None) -> list[int]:
    raise NotImplementedError("TODO")


def inorder_recursive(root: TreeNode | None) -> list[int]:
    raise NotImplementedError("TODO")


def postorder_recursive(root: TreeNode | None) -> list[int]:
    raise NotImplementedError("TODO")


def preorder_iterative(root: TreeNode | None) -> list[int]:
    raise NotImplementedError("TODO")


def inorder_iterative(root: TreeNode | None) -> list[int]:
    raise NotImplementedError("TODO")


def postorder_iterative(root: TreeNode | None) -> list[int]:
    raise NotImplementedError("TODO")


def postorder_two_stack(root: TreeNode | None) -> list[int]:
    raise NotImplementedError("TODO")


def traverse_unified(root: TreeNode | None, order: str) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    root = build([1, 2, 3, 4, 5, None, 6])
    print(render(root))
    for name, rec, it in [("pre ", preorder_recursive, preorder_iterative),
                          ("in  ", inorder_recursive, inorder_iterative),
                          ("post", postorder_recursive, postorder_iterative)]:
        print(f"{name} recursive={rec(root)} iterative={it(root)} "
              f"unified={traverse_unified(root, name.strip())}")
    print("post two-stack:", postorder_two_stack(root))
    print("empty:", preorder_iterative(None), inorder_iterative(None), postorder_iterative(None))
    long = chain(list(range(100_000)), side="left")
    try:
        inorder_recursive(long)
    except RecursionError:
        print("recursive inorder on 100000-node chain -> RecursionError")
    print("iterative inorder first/last:", inorder_iterative(long)[0], inorder_iterative(long)[-1])


if __name__ == "__main__":
    main()
