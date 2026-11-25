"""
Exercise 10 — BST Search, Insert, Delete and Validate             [Tier: ★ Core]
Chapter 14 · Pattern: BST ordering; bounds passed down · Target time: 30 min

Problem
-------
A binary search tree (BST) with distinct keys: every key in a node's LEFT subtree
is smaller than the node's key and every key in its RIGHT subtree is larger.
(a) search(root, key) -> node or None;
(b) insert(root, key) -> root (ignore a key that is already present);
(c) delete(root, key) -> root (no-op if the key is absent);
(d) is_valid_bst(root) -> bool for an arbitrary binary tree.

Examples
--------
>>> root = build([5, 3, 6, 2, 4, None, 7])
>>> to_level(delete(root, 3))
[5, 4, 6, 2, None, None, 7]
>>> is_valid_bst(build([5, 1, 6, None, None, 3, 7]))    # 3 sits right of 5
False

Constraints
-----------
- 0 <= n <= 10**4; keys are ints. Strict ordering (no duplicates).
- Sorted inserts build a chain of height n, so the recursive delete and
  is_valid_bst need height <= ~900 (1,000-frame limit). Also write
  delete_iterative and is_valid_bst_iterative, which handle any height.

Approach ladder
---------------
Search / insert: walk down one path, left if smaller, right if larger.
   O(h) time: O(log n) when balanced, O(n) for sorted-order inserts. Loops, O(1)
   space.
Delete: find the node; 0 children -> remove it, 1 child -> splice the child up,
   2 children -> copy in the inorder SUCCESSOR (leftmost key of the right
   subtree), then delete that key from the right subtree. O(h).
   delete_iterative: walk down keeping the parent; for 2 children, copy the
   successor's key up and splice the successor out instead. O(h), O(1) space.
Validate:
1. Brute force — inorder traversal must be strictly increasing. O(n) time,
   O(n) for the list (or O(h) if you compare with the previous value on the fly).
2. Bounds (optimal) — pass an open interval (low, high) down: the left child
   inherits (low, node.val), the right (node.val, high). O(n) time, O(h) stack.
3. Same bounds on an explicit stack of (node, low, high): any height.

Hints
-----
- Use None (or -inf/inf) for "no bound yet" so any int key is allowed at the root.
- Delete is easiest recursively: `node.left = delete(node.left, key)`.

Edge cases
----------
- Empty tree for all four; delete the root; delete a node with two children
  whose successor has a right child; keys equal to a bound (invalid).

Wrong-but-tempting
------------------
- Validating with only the direct children (left.val < val < right.val): a key
  deep in the right subtree can still be smaller than an ancestor. The tree
  [5, 1, 6, None, None, 3, 7] passes the local test but is not a BST.
- Using float('-inf') with `<=`: allows duplicates; the strict test is `<`.
- Delete with two children by removing the node and re-inserting a whole subtree:
  correct but O(n) and changes the shape.

Follow-ups
----------
- Keep the tree balanced (AVL / red-black) — know the names and O(log n) bounds;
  in Python, use a sorted list + `bisect` for small data (→ §11.2).
- Range sum / count in [lo, hi]: prune subtrees that lie fully outside.
"""
from __future__ import annotations

from treenode import TreeNode, build, chain, inorder_values, render, to_level


def search(root: TreeNode | None, key: int) -> TreeNode | None:
    node = root
    while node and node.val != key:
        node = node.left if key < node.val else node.right
    return node


def insert(root: TreeNode | None, key: int) -> TreeNode:
    if root is None:
        return TreeNode(key)
    node = root
    while True:
        if key == node.val:
            return root                        # already present
        if key < node.val:
            if node.left is None:
                node.left = TreeNode(key)
                return root
            node = node.left
        else:
            if node.right is None:
                node.right = TreeNode(key)
                return root
            node = node.right


def delete(root: TreeNode | None, key: int) -> TreeNode | None:
    if root is None:
        return None
    if key < root.val:
        root.left = delete(root.left, key)
    elif key > root.val:
        root.right = delete(root.right, key)
    else:
        if root.left is None:                  # 0 or 1 child: splice
            return root.right
        if root.right is None:
            return root.left
        succ = root.right                      # 2 children: inorder successor
        while succ.left:
            succ = succ.left
        root.val = succ.val
        root.right = delete(root.right, succ.val)
    return root


def delete_iterative(root: TreeNode | None, key: int) -> TreeNode | None:
    parent, node = None, root
    while node and node.val != key:
        parent, node = node, (node.left if key < node.val else node.right)
    if node is None:
        return root                            # key absent
    if node.left and node.right:               # 2 children: successor's key moves up
        parent, succ = node, node.right
        while succ.left:
            parent, succ = succ, succ.left
        node.val = succ.val
        node = succ                            # now remove succ (no left child)
    child = node.left or node.right            # 0 or 1 child: splice it up
    if parent is None:
        return child
    if parent.left is node:
        parent.left = child
    else:
        parent.right = child
    return root


def is_valid_brute(root: TreeNode | None) -> bool:
    vals = inorder_values(root)
    return all(a < b for a, b in zip(vals, vals[1:]))


def is_valid_bst(root: TreeNode | None, low: int | None = None,
                 high: int | None = None) -> bool:
    if root is None:
        return True
    if (low is not None and root.val <= low) or (high is not None and root.val >= high):
        return False
    return (is_valid_bst(root.left, low, root.val)        # left: below this key
            and is_valid_bst(root.right, root.val, high))  # right: above it


def is_valid_bst_iterative(root: TreeNode | None) -> bool:
    stack: list[tuple[TreeNode, int | None, int | None]] = [(root, None, None)] if root else []
    while stack:
        node, low, high = stack.pop()
        if (low is not None and node.val <= low) or (high is not None and node.val >= high):
            return False
        if node.left:
            stack.append((node.left, low, node.val))
        if node.right:
            stack.append((node.right, node.val, high))
    return True


def is_valid_local_only(root: TreeNode | None) -> bool:
    """WRONG: checks each node against its direct children only."""
    if root is None:
        return True
    if root.left and root.left.val >= root.val:
        return False
    if root.right and root.right.val <= root.val:
        return False
    return is_valid_local_only(root.left) and is_valid_local_only(root.right)


def main() -> None:
    root = None
    for k in [5, 3, 6, 2, 4, 7, 4]:
        root = insert(root, k)
    print(render(root))
    print("search 4:", search(root, 4), "| search 8:", search(root, 8))
    for k in (3, 5, 42):
        root = delete(root, k)
        print(f"delete {k:<2} -> level {to_level(root)}  inorder {inorder_values(root)}")
    trap = build([5, 1, 6, None, None, 3, 7])
    print(render(trap))
    print("local-only check:", is_valid_local_only(trap), "| bounds:", is_valid_bst(trap),
          "| inorder:", inorder_values(trap))
    for lst in ([], [2, 2], [2, 1, 3], [-2**31, None, 2**31 - 1]):
        print(f"valid {lst!s:<26} bounds={is_valid_bst(build(lst))} brute={is_valid_brute(build(lst))}")
    deep = chain(list(range(10_000)))          # what sorted inserts produce
    for k in (0, 5_000, 9_999):
        deep = delete_iterative(deep, k)
    print("10,000-node chain: iterative valid =", is_valid_bst_iterative(deep),
          "| keys left =", len(inorder_values(deep)))


if __name__ == "__main__":
    main()
