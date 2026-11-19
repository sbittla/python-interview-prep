"""Shared binary-tree helpers for Chapter 14 (imported by the tree exercises).

    TreeNode(val, left, right)  one node; __slots__, repr shows the value only
    build(level)                level-order list with None holes -> root  ([1, None, 2] style)
    to_level(root)              root -> level-order list with None holes, trailing Nones trimmed
    render(root)                multi-line ASCII drawing, root on top
    inorder_values(root)        inorder list of values (iterative, any depth)
    random_tree(rng, n, ...)    random shape with n nodes (tests)
    random_bst(rng, n, ...)     random BST with n distinct keys (tests)
    chain(values, side)         degenerate "linked list" tree, for depth tests

All helpers are iterative, so they work on trees deeper than the recursion limit.
"""
from __future__ import annotations

import random
from collections import deque
from collections.abc import Sequence


class TreeNode:
    __slots__ = ("val", "left", "right")

    def __init__(self, val: int = 0, left: TreeNode | None = None,
                 right: TreeNode | None = None) -> None:
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self) -> str:            # value only, never the address
        return f"TreeNode({self.val!r})"


def build(level: Sequence[int | None]) -> TreeNode | None:
    """Level-order list -> tree. None marks a missing child of a node that exists."""
    if not level or level[0] is None:
        return None
    root = TreeNode(level[0])
    queue = deque([root])
    i = 1
    while queue and i < len(level):
        node = queue.popleft()
        if i < len(level) and level[i] is not None:
            node.left = TreeNode(level[i])
            queue.append(node.left)
        i += 1
        if i < len(level) and level[i] is not None:
            node.right = TreeNode(level[i])
            queue.append(node.right)
        i += 1
    return root


def to_level(root: TreeNode | None) -> list[int | None]:
    out: list[int | None] = []
    queue: deque[TreeNode | None] = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def inorder_values(root: TreeNode | None) -> list[int]:
    out: list[int] = []
    stack: list[TreeNode] = []
    node = root
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        out.append(node.val)
        node = node.right
    return out


def render(root: TreeNode | None) -> str:
    """Draw the tree top-down. Column = inorder rank, row = depth."""
    if root is None:
        return "(empty)"
    order: list[TreeNode] = []           # inorder, gives each node its column
    depth: dict[int, int] = {id(root): 0}
    stack: list[TreeNode] = []
    node = root
    while stack or node:
        while node:
            stack.append(node)
            for child in (node.left, node.right):
                if child:
                    depth[id(child)] = depth[id(node)] + 1
            node = node.left
        node = stack.pop()
        order.append(node)
        node = node.right
    width = max(len(str(n.val)) for n in order)
    col = {id(n): i * (width + 1) for i, n in enumerate(order)}
    height = max(depth.values()) + 1
    total = len(order) * (width + 1) + 1
    rows = [[" "] * total for _ in range(2 * height)]
    for n in order:
        x, d = col[id(n)], depth[id(n)]
        label = str(n.val)
        rows[2 * d][x:x + len(label)] = list(label)
        if n.left:
            lx = col[id(n.left)] + len(str(n.left.val))
            rows[2 * d + 1][lx] = "/"
            for c in range(lx + 1, x):
                rows[2 * d][c] = "_"
        if n.right:
            rx = col[id(n.right)] - 1
            rows[2 * d + 1][rx] = "\\"
            for c in range(x + len(label), rx):
                rows[2 * d][c] = "_"
    lines = ["".join(r).rstrip() for r in rows]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def random_tree(rng: random.Random, n: int, lo: int = -9, hi: int = 9,
                distinct: bool = False) -> TreeNode | None:
    """Random shape: each new node hangs off a random free slot."""
    if n == 0:
        return None
    vals = rng.sample(range(lo, hi + 1), n) if distinct else [rng.randint(lo, hi) for _ in range(n)]
    root = TreeNode(vals[0])
    open_slots: list[tuple[TreeNode, str]] = [(root, "left"), (root, "right")]
    for v in vals[1:]:
        parent, side = open_slots.pop(rng.randrange(len(open_slots)))
        child = TreeNode(v)
        if side == "left":
            parent.left = child
        else:
            parent.right = child
        open_slots += [(child, "left"), (child, "right")]
    return root


def random_bst(rng: random.Random, n: int, lo: int = 0, hi: int = 99) -> TreeNode | None:
    keys = rng.sample(range(lo, hi + 1), n)
    root: TreeNode | None = None
    for k in keys:
        if root is None:
            root = TreeNode(k)
            continue
        node = root
        while True:
            if k < node.val:
                if node.left is None:
                    node.left = TreeNode(k)
                    break
                node = node.left
            else:
                if node.right is None:
                    node.right = TreeNode(k)
                    break
                node = node.right
    return root


def chain(values: Sequence[int], side: str = "right") -> TreeNode | None:
    root: TreeNode | None = None
    for v in reversed(values):
        root = TreeNode(v, root, None) if side == "left" else TreeNode(v, None, root)
    return root


if __name__ == "__main__":
    t = build([4, 2, 6, 1, 3, 5, 7])
    print(render(t))
    print(to_level(build([1, None, 2, 3])))
