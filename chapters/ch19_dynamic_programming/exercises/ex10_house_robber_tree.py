"""
Exercise 10 — House Robber on a Tree (DP on trees)                  [Tier: ◆ Extended]
Chapter 19 · Pattern: tree DP, (take, skip) pair per node · Target time: 30 min

Problem
-------
Houses form a binary tree; node.val >= 0 is the cash inside. Robbing a node and its
parent (directly linked houses) trips the alarm. Return the most cash you can take.
`build(values)` makes a tree from a level-order list with None for missing children.

Examples
--------
>>> rob_tree(build([3, 2, 3, None, 3, None, 1]))
7
>>> rob_tree(build([3, 4, 5, 1, 3, None, 1]))
9
>>> rob_tree(None)
0

Constraints
-----------
- 0 <= nodes <= 10^4, 0 <= val <= 10^4. The tree may be a 10^4-deep chain.

Hints
-----
- The "take" value of a node needs the children's "skip" values; return both.
- Don't bump sys.setrecursionlimit in an interview answer; switch to an explicit order.

Follow-ups
----------
- Maximum independent set on a general tree (any number of children): same pair DP.
- Minimum cameras to cover a tree: three states per node instead of two.
"""
from __future__ import annotations

from collections import deque


class TreeNode:
    __slots__ = ("val", "left", "right")

    def __init__(self, val: int, left: TreeNode | None = None,
                 right: TreeNode | None = None) -> None:
        self.val, self.left, self.right = val, left, right


def build(values: list[int | None]) -> TreeNode | None:
    """Level-order list (None = no child) -> tree. Helper, not part of the exercise."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue, i = deque([root]), 1
    while queue and i < len(values):
        node = queue.popleft()
        for side in ("left", "right"):
            if i < len(values) and values[i] is not None:
                child = TreeNode(values[i])
                setattr(node, side, child)
                queue.append(child)
            i += 1
    return root


def chain(n: int) -> TreeNode | None:
    """A right-leaning chain 1, 2, ..., n (depth n). Helper for deep-tree demos."""
    root = None
    for v in range(n, 0, -1):
        root = TreeNode(v, right=root)
    return root


def _grandchildren(node: TreeNode) -> list[TreeNode | None]:
    return [g for c in (node.left, node.right) if c for g in (c.left, c.right)]


def rob_tree_brute(root: TreeNode | None) -> int:
    raise NotImplementedError("TODO")


def rob_tree_memo(root: TreeNode | None) -> int:
    raise NotImplementedError("TODO")


def rob_tree_pair(root: TreeNode | None) -> int:
    raise NotImplementedError("TODO")


def rob_tree(root: TreeNode | None) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    for values in ([3, 2, 3, None, 3, None, 1], [3, 4, 5, 1, 3, None, 1], [5], [],
                   [4, 1, None, 2, None, 3]):
        root = build(values)
        rungs = (rob_tree_brute(root), rob_tree_memo(root), rob_tree_pair(root), rob_tree(root))
        print(f"rob_tree({values}) = {rungs[-1]}  rungs agree: {len(set(rungs)) == 1}")
    deep = chain(10_000)
    print("10,000-deep chain, iterative:", rob_tree(deep))
    try:
        rob_tree_pair(deep)
    except RecursionError:
        print("10,000-deep chain, recursive pair: RecursionError")


if __name__ == "__main__":
    main()
