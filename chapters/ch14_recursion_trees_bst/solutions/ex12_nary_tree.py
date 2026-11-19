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

Approach ladder
---------------
Everything from the binary-tree sections carries over; replace "left, right"
with "for child in node.children":
- depth: 1 + max(child depths), with `default=0` for leaves. O(n), O(h) stack;
  or BFS counting levels, O(n) time, O(w) queue.
- level order: the same `len(queue)` BFS. O(n).
- preorder: pop, record, push children REVERSED. Postorder: record in
  (node, children right-to-left) order, then reverse the whole list. O(n).
- Binary encoding ("left-child, right-sibling"): any rooted ordered tree becomes
  a binary tree with the same node count, so binary-tree code (serialize, ex09)
  applies. O(n) both ways.

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
    if root is None:
        return 0
    return 1 + max((max_depth(c) for c in root.children), default=0)


def max_depth_bfs(root: Node | None) -> int:
    return len(level_order(root))


def level_order(root: Node | None) -> list[list[int]]:
    levels: list[list[int]] = []
    queue = deque([root] if root else [])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            queue.extend(node.children)
        levels.append(level)
    return levels


def preorder(root: Node | None) -> list[int]:
    out: list[int] = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        stack.extend(reversed(node.children))   # first child popped first
    return out


def postorder(root: Node | None) -> list[int]:
    out: list[int] = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)                    # node, last child ... first child
        stack.extend(node.children)
    return out[::-1]


def to_binary(root: Node | None) -> TreeNode | None:
    if root is None:
        return None
    broot = TreeNode(root.val)
    stack = [(root, broot)]
    while stack:
        node, bnode = stack.pop()
        prev = None
        for child in node.children:
            bchild = TreeNode(child.val)
            if prev is None:
                bnode.left = bchild             # first child -> left
            else:
                prev.right = bchild             # next sibling -> right
            prev = bchild
            stack.append((child, bchild))
    return broot


def from_binary(broot: TreeNode | None) -> Node | None:
    if broot is None:
        return None
    root = Node(broot.val)
    stack = [(broot, root)]
    while stack:
        bnode, node = stack.pop()
        b = bnode.left
        while b:                                # walk the sibling chain
            child = Node(b.val)
            node.children.append(child)
            stack.append((b, child))
            b = b.right
    return root


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
