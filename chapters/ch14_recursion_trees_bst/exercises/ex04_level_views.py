"""
Exercise 04 — Level Order, Zigzag and Right-Side View             [Tier: ★ Core]
Chapter 14 · Pattern: BFS by level · Target time: 20 min

Problem
-------
For a binary tree return
(a) level_order: a list of levels, each a list of values left to right;
(b) zigzag: the same, but every second level (the 2nd, 4th, ...) right to left;
(c) right_view: the last value of each level (what you see from the right).

Examples
--------
>>> root = build([3, 9, 20, None, None, 15, 7])
>>> level_order(root)
[[3], [9, 20], [15, 7]]
>>> zigzag(root)
[[3], [20, 9], [15, 7]]
>>> right_view(build([1, 2, 3, None, 5]))
[1, 3, 5]

Constraints
-----------
- 0 <= n <= 10**5.

Hints
-----
- `for _ in range(len(queue)):` freezes the level size before children are added.
- Use collections.deque, not list.pop(0) (O(n) per pop).

Edge cases
----------
- Empty tree -> []; single node; left-only chain (right view is the whole chain).

Wrong-but-tempting
------------------
- Right view = "keep going right from the root": misses a left subtree that is
  deeper than the right one ([1, 2, 3, 4] -> view is [1, 3, 4]).
- Zigzag by swapping the order you enqueue children: corrupts the next level.

Follow-ups
----------
- Left view, level averages, largest value per level: change one line.
- Bottom-up level order: reverse the result list at the end.
"""
from __future__ import annotations

from collections import deque

from treenode import TreeNode, build, render


def level_order_dfs(root: TreeNode | None) -> list[list[int]]:
    raise NotImplementedError("TODO")


def level_order(root: TreeNode | None) -> list[list[int]]:
    raise NotImplementedError("TODO")


def zigzag(root: TreeNode | None) -> list[list[int]]:
    raise NotImplementedError("TODO")


def right_view(root: TreeNode | None) -> list[int]:
    raise NotImplementedError("TODO")


def right_view_dfs(root: TreeNode | None) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    root = build([3, 9, 20, None, None, 15, 7])
    print(render(root))
    print("level order:", level_order(root), "| dfs:", level_order_dfs(root))
    print("zigzag     :", zigzag(root))
    for lst in ([1, 2, 3, None, 5], [1, 2, 3, 4], [], [1, 2, None, 3]):
        t = build(lst)
        print(f"right view of {lst!s:<20} bfs={right_view(t)} dfs={right_view_dfs(t)}")


if __name__ == "__main__":
    main()
