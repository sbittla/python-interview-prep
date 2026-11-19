"""
Exercise 12 — N-ary Trees: Depth, Level Order, Traversals, Binary Encoding   [Tier: ◆ Extended]
Chapter 14 · Pattern: same templates, a loop over children · Target time: 20 min

Problem
-------
A node of an N-ary tree has a value and a list of children (possibly empty).
(a) max_depth(root): number of nodes on the longest root-to-leaf path;
(b) level_order(root): list of levels;
(c) preorder(root) and postorder(root), iteratively;
(d) to_binary(root) / from_binary(b): encode the N-ary tree as a binary tree
    (left = first child, right = next sibling) and decode it back.

Examples
--------
>>> t = from_nested((1, [(3, [(5, []), (6, [])]), (2, []), (4, [])]))
>>> max_depth(t), level_order(t)
(3, [[1], [3, 2, 4], [5, 6]])
>>> preorder(t), postorder(t)
([1, 3, 5, 6, 2, 4], [5, 6, 3, 2, 4, 1])

Constraints
-----------
- 0 <= n <= 10**4; depth up to 1,000 for the recursive version.

Hints
-----
- `max((depth(c) for c in children), default=0)` avoids a ValueError on leaves.

Edge cases
----------
- Empty tree; single node; one node with 1,000 children (wide, shallow).

Wrong-but-tempting
------------------
- Preorder pushing children in natural order: visits the LAST child first.
- Treating "no children" as `children is None` in one place and `[]` in another.

Follow-ups
----------
- Serialize an N-ary tree: write each value followed by its child count, or
  value, children..., then a ')' marker.
- Diameter of an N-ary tree: keep the two largest child heights at each node.
"""
from __future__ import annotations

from collections import deque

from treenode import TreeNode, render


class Node:
    __slots__ = ("val", "children")

    def __init__(self, val: int, children: list[Node] | None = None) -> None:
        self.val = val
        self.children = children if children is not None else []

    def __repr__(self) -> str:
        return f"Node({self.val!r})"


def from_nested(spec: tuple | None) -> Node | None:
    """(val, [child_spec, ...]) -> Node; built with a stack (any depth)."""
    if spec is None:
        return None
    root = Node(spec[0])
    stack = [(root, spec[1])]
    while stack:
        node, kids = stack.pop()
        for val, grandkids in kids:
            child = Node(val)
            node.children.append(child)
            stack.append((child, grandkids))
    return root


def to_nested(root: Node | None) -> tuple | None:
    if root is None:
        return None
    return (root.val, [to_nested(c) for c in root.children])


def max_depth(root: Node | None) -> int:
    raise NotImplementedError("TODO")


def max_depth_bfs(root: Node | None) -> int:
    raise NotImplementedError("TODO")


def level_order(root: Node | None) -> list[list[int]]:
    raise NotImplementedError("TODO")


def preorder(root: Node | None) -> list[int]:
    raise NotImplementedError("TODO")


def postorder(root: Node | None) -> list[int]:
    raise NotImplementedError("TODO")


def to_binary(root: Node | None) -> TreeNode | None:
    raise NotImplementedError("TODO")


def from_binary(broot: TreeNode | None) -> Node | None:
    raise NotImplementedError("TODO")


def main() -> None:
    spec = (1, [(3, [(5, []), (6, [])]), (2, []), (4, [])])
    t = from_nested(spec)
    print("depth:", max_depth(t), max_depth_bfs(t), "| levels:", level_order(t))
    print("preorder:", preorder(t), "| postorder:", postorder(t))
    b = to_binary(t)
    print("left-child right-sibling encoding:")
    print(render(b))
    print("decodes back:", to_nested(from_binary(b)) == spec)
    wide = Node(0, [Node(i) for i in range(1, 1001)])
    print("wide tree: depth", max_depth(wide), "level sizes", [len(l) for l in level_order(wide)])
    print("empty:", max_depth(None), level_order(None), preorder(None), postorder(None))


if __name__ == "__main__":
    main()
