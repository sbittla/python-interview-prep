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

Approach ladder
---------------
1. DFS with depth — preorder carrying `depth`; append to levels[depth]. O(n) time,
   O(h) stack. Works, but recursion depth can fail on chains, and the "level"
   idea is hidden.
2. BFS by level (optimal) — a deque; at the top of each round, `len(queue)` is
   exactly the width of the current level, so process that many nodes. O(n) time,
   O(w) space (w = max width, up to n/2).
   Zigzag: build the level normally and reverse every odd one (or append to a
   deque's left). Right view: last node of each round.
3. Right view by DFS — visit right child first; the first node seen at each new
   depth is visible. O(h) extra space: better than BFS on wide, shallow trees.

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
    levels: list[list[int]] = []

    def visit(node: TreeNode | None, depth: int) -> None:
        if node is None:
            return
        if depth == len(levels):
            levels.append([])
        levels[depth].append(node.val)
        visit(node.left, depth + 1)
        visit(node.right, depth + 1)

    visit(root, 0)
    return levels


def level_order(root: TreeNode | None) -> list[list[int]]:
    levels: list[list[int]] = []
    queue = deque([root] if root else [])
    while queue:
        level = []
        for _ in range(len(queue)):        # exactly the nodes of this level
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level)
    return levels


def zigzag(root: TreeNode | None) -> list[list[int]]:
    return [lvl if d % 2 == 0 else lvl[::-1] for d, lvl in enumerate(level_order(root))]


def right_view(root: TreeNode | None) -> list[int]:
    return [lvl[-1] for lvl in level_order(root)]


def right_view_dfs(root: TreeNode | None) -> list[int]:
    view: list[int] = []
    stack = [(root, 0)] if root else []
    while stack:
        node, depth = stack.pop()
        if depth == len(view):
            view.append(node.val)          # first node met at this depth
        if node.left:
            stack.append((node.left, depth + 1))
        if node.right:
            stack.append((node.right, depth + 1))   # popped first: right-first DFS
    return view


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
