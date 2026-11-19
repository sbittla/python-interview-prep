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

Approach ladder
---------------
Recipe — state: best(node) = most cash from node's subtree; transition:
max(node.val + best(the four grandchildren), best(left) + best(right)); base:
best(None) = 0; order: children before parents (post-order); answer: best(root).
1. Plain recursion — every node is recomputed from its parent and its grandparent:
   exponential, O(phi^h)-style blow-up on chains (O(n) stack).
2. Memoised — dict keyed by the node object (default identity hash): O(n) time and
   space.
3. Pair recursion — return (take, skip) for each node: take = val + skip(L) +
   skip(R), skip = max(L) + max(R). Each node visited once, no dict: O(n) time,
   O(h) stack. Still recursive: a 10^4-deep chain exceeds the default ~1000 limit
   (section 7.21).
4. Iterative — list nodes in BFS order, then process that list in reverse (children
   always come after their parent in BFS order): O(n) time, O(n) space, no recursion.

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
    if root is None:
        return 0
    take = root.val + sum(rob_tree_brute(g) for g in _grandchildren(root))
    skip = rob_tree_brute(root.left) + rob_tree_brute(root.right)
    return max(take, skip)


def rob_tree_memo(root: TreeNode | None) -> int:
    memo: dict[TreeNode, int] = {}              # fresh per call; never a default argument

    def best(node: TreeNode | None) -> int:
        if node is None:
            return 0
        if node not in memo:
            take = node.val + sum(best(g) for g in _grandchildren(node))
            memo[node] = max(take, best(node.left) + best(node.right))
        return memo[node]

    return best(root)


def rob_tree_pair(root: TreeNode | None) -> int:
    def pair(node: TreeNode | None) -> tuple[int, int]:     # (take node, skip node)
        if node is None:
            return 0, 0
        lt, ls = pair(node.left)
        rt, rs = pair(node.right)
        return node.val + ls + rs, max(lt, ls) + max(rt, rs)

    return max(pair(root))


def rob_tree(root: TreeNode | None) -> int:
    if root is None:
        return 0
    order = [root]
    for node in order:                          # BFS: parents before children
        order.extend(c for c in (node.left, node.right) if c)
    take: dict[TreeNode, int] = {}
    skip: dict[TreeNode, int] = {}
    for node in reversed(order):                # children before parents
        kids = [c for c in (node.left, node.right) if c]
        take[node] = node.val + sum(skip[c] for c in kids)
        skip[node] = sum(max(take[c], skip[c]) for c in kids)
    return max(take[root], skip[root])


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
