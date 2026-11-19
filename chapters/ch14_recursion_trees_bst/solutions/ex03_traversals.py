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

Approach ladder
---------------
1. Recursive — three lines each; O(n) time, O(h) call stack; RecursionError once
   h passes ~1,000 (→ §7.21).
2. Iterative, one idiom per order —
   preorder: pop, record, push right then left (so left is processed first);
   inorder: "go left as far as possible, pop, record, turn right";
   postorder: same walk as inorder but only record a node once its right subtree
   is done (track the last node recorded). O(n) time, O(h) stack.
   Two-stack shortcut for postorder: do "node, right, left" and reverse.
3. Unified — push (node, visited) pairs; an unvisited node re-pushes itself
   between its children in the order you want. One template, all three orders.

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
    return [] if root is None else [root.val, *preorder_recursive(root.left),
                                    *preorder_recursive(root.right)]


def inorder_recursive(root: TreeNode | None) -> list[int]:
    return [] if root is None else [*inorder_recursive(root.left), root.val,
                                    *inorder_recursive(root.right)]


def postorder_recursive(root: TreeNode | None) -> list[int]:
    return [] if root is None else [*postorder_recursive(root.left),
                                    *postorder_recursive(root.right), root.val]


def preorder_iterative(root: TreeNode | None) -> list[int]:
    out: list[int] = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        if node.right:
            stack.append(node.right)      # pushed first, popped last
        if node.left:
            stack.append(node.left)
    return out


def inorder_iterative(root: TreeNode | None) -> list[int]:
    out: list[int] = []
    stack: list[TreeNode] = []
    node = root
    while stack or node:
        while node:                       # go left as far as possible
            stack.append(node)
            node = node.left
        node = stack.pop()                # leftmost unvisited node
        out.append(node.val)
        node = node.right                 # then its right subtree
    return out


def postorder_iterative(root: TreeNode | None) -> list[int]:
    out: list[int] = []
    stack: list[TreeNode] = []
    node, last = root, None
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        top = stack[-1]
        if top.right and top.right is not last:
            node = top.right              # right subtree not done yet
        else:
            out.append(top.val)           # both subtrees done
            last = stack.pop()
    return out


def postorder_two_stack(root: TreeNode | None) -> list[int]:
    out: list[int] = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)              # node, right, left ...
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    return out[::-1]                      # ... reversed = left, right, node


def traverse_unified(root: TreeNode | None, order: str) -> list[int]:
    out: list[int] = []
    stack: list[tuple[TreeNode | None, bool]] = [(root, False)]
    while stack:
        node, visited = stack.pop()
        if node is None:
            continue
        if visited:
            out.append(node.val)
            continue
        # push in REVERSE of the wanted order
        if order == "pre":
            stack += [(node.right, False), (node.left, False), (node, True)]
        elif order == "in":
            stack += [(node.right, False), (node, True), (node.left, False)]
        else:
            stack += [(node, True), (node.right, False), (node.left, False)]
    return out


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
