"""
Exercise 06 — Path Sums: Root-to-Leaf, Downward, and Max Path Sum   [Tier: ◆ Extended]
Chapter 14 · Pattern: DFS + backtracking; return info up the tree · Target time: 30 min

Problem
-------
Node values may be negative.
(a) root_to_leaf_paths(root, target): every root-to-leaf path (list of values)
    whose sum is target, in left-to-right order.
(b) count_downward_paths(root, target): how many paths that go strictly downward
    (start anywhere, end anywhere below or at the start) sum to target.
(c) max_path_sum(root): the largest sum of any non-empty path; a path is a
    sequence of nodes joined by edges, each node used at most once, and need
    not pass through the root.

Examples
--------
>>> t = build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1])
>>> root_to_leaf_paths(t, 22)
[[5, 4, 11, 2], [5, 8, 4, 5]]
>>> max_path_sum(build([-10, 9, 20, None, None, 15, 7]))
42

Constraints
-----------
- 1 <= n <= 10**4 for (c); 0 <= n for (a), (b). |val| <= 1000.

Approach ladder
---------------
(a) Enumerate all root-to-leaf paths, filter by sum: O(n * h). Better: DFS with
    ONE shared path list — append on entry, pop on exit (backtracking, → §18.1),
    copy only when a leaf matches. Still O(n * h) worst case (copies), O(h) extra.
(b) Brute: from every node, walk every downward path: O(n * h). Optimal: prefix
    sums on the current root path (→ §10.9): paths ending here with sum
    t = number of earlier prefixes equal to (running - t). Counter + backtrack.
    O(n) time, O(h) space.
(c) Brute: for every pair of nodes, sum the path between them: O(n^2 * h).
    Optimal, return info up the tree: each call returns the best DOWNWARD gain
    starting at the node, max(0, child gains) + val; the best path that BENDS at
    the node is val + left_gain + right_gain. O(n) time, O(h) stack.

Hints
-----
- (c) Clamp a child's gain at 0: a negative branch is better left out.
- (c) All-negative tree: the answer is the largest single value, not 0.

Edge cases
----------
- Single negative node; all negative values; target reachable only by a non-leaf
  prefix (must NOT count for (a)); empty tree for (a)/(b).

Wrong-but-tempting
------------------
- (a) Appending `path` instead of `path[:]`: every result is the same (now empty)
  list object.
- (a) Testing the sum at a None child instead of at a leaf: counts a one-child
  node's path twice and accepts non-leaf endings.
- (c) Returning `val + left + right` to the parent: a parent cannot use a path
  that already bends.
- (c) Initialising best = 0: wrong for all-negative trees.

Follow-ups
----------
- Return the path itself for (c): return (gain, node list) instead of a number.
"""
from __future__ import annotations

from collections import Counter

from treenode import TreeNode, build, render


def root_to_leaf_paths_brute(root: TreeNode | None, target: int) -> list[list[int]]:
    paths: list[list[int]] = []
    stack = [(root, [root.val])] if root else []
    while stack:
        node, path = stack.pop()
        if not node.left and not node.right:
            paths.append(path)
        for child in (node.right, node.left):
            if child:
                stack.append((child, path + [child.val]))
    return [p for p in paths if sum(p) == target]


def root_to_leaf_paths(root: TreeNode | None, target: int) -> list[list[int]]:
    found: list[list[int]] = []
    path: list[int] = []

    def dfs(node: TreeNode | None, remaining: int) -> None:
        if node is None:
            return
        path.append(node.val)
        remaining -= node.val
        if node.left is None and node.right is None and remaining == 0:
            found.append(path[:])             # copy: path keeps changing
        dfs(node.left, remaining)
        dfs(node.right, remaining)
        path.pop()                            # backtrack

    dfs(root, target)
    return found


def count_downward_brute(root: TreeNode | None, target: int) -> int:
    def from_here(node: TreeNode | None, need: int) -> int:
        if node is None:
            return 0
        return (node.val == need) + from_here(node.left, need - node.val) \
            + from_here(node.right, need - node.val)

    def every(node: TreeNode | None) -> int:
        return 0 if node is None else from_here(node, target) + every(node.left) + every(node.right)

    return every(root)


def count_downward_paths(root: TreeNode | None, target: int) -> int:
    seen = Counter({0: 1})                    # prefix sums on the current root path

    def dfs(node: TreeNode | None, running: int) -> int:
        if node is None:
            return 0
        running += node.val
        hits = seen[running - target]         # paths ending at this node
        seen[running] += 1
        hits += dfs(node.left, running) + dfs(node.right, running)
        seen[running] -= 1                    # backtrack: leave this branch
        return hits

    return dfs(root, 0)


def max_path_sum_brute(root: TreeNode) -> int:
    parent: dict[int, TreeNode | None] = {id(root): None}
    depth: dict[int, int] = {id(root): 0}
    nodes, stack = [], [root]
    while stack:
        node = stack.pop()
        nodes.append(node)
        for c in (node.left, node.right):
            if c:
                parent[id(c)], depth[id(c)] = node, depth[id(node)] + 1
                stack.append(c)

    def path_sum(a: TreeNode, b: TreeNode) -> int:
        total = 0
        while a is not b:                     # climb the deeper one until they meet
            if depth[id(a)] < depth[id(b)]:
                a, b = b, a
            total += a.val
            a = parent[id(a)]
        return total + a.val

    return max(path_sum(a, b) for i, a in enumerate(nodes) for b in nodes[i:])


def max_path_sum(root: TreeNode) -> int:
    def gain(node: TreeNode | None) -> tuple[int, int]:
        """(best downward path starting here, best path anywhere in subtree)"""
        if node is None:
            return 0, -10**18
        lg, lbest = gain(node.left)
        rg, rbest = gain(node.right)
        lg, rg = max(lg, 0), max(rg, 0)       # drop negative branches
        bend = node.val + lg + rg             # path that turns at this node
        return node.val + max(lg, rg), max(lbest, rbest, bend)

    return gain(root)[1]


def main() -> None:
    t = build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1])
    print(render(t))
    print("root-to-leaf = 22:", root_to_leaf_paths(t, 22), "| brute:", root_to_leaf_paths_brute(t, 22))
    print("downward paths = 22:", count_downward_paths(t, 22), "| brute:", count_downward_brute(t, 22))
    for lst in ([-10, 9, 20, None, None, 15, 7], [1, 2, 3], [-3], [-2, -1, -5], [2, -1, -2]):
        r = build(lst)
        print(f"max path sum {lst!s:<28} -> {max_path_sum(r):>3}  brute {max_path_sum_brute(r):>3}")


if __name__ == "__main__":
    main()
