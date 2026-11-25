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
- The recursive versions need tree height <= ~900 (CPython's 1,000-frame
  limit). max_path_sum_iterative handles any shape, e.g. a 10**4-node chain.

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

from treenode import TreeNode, build, chain, render


def root_to_leaf_paths_brute(root: TreeNode | None, target: int) -> list[list[int]]:
    raise NotImplementedError("TODO")


def root_to_leaf_paths(root: TreeNode | None, target: int) -> list[list[int]]:
    raise NotImplementedError("TODO")


def count_downward_brute(root: TreeNode | None, target: int) -> int:
    raise NotImplementedError("TODO")


def count_downward_paths(root: TreeNode | None, target: int) -> int:
    raise NotImplementedError("TODO")


def max_path_sum_brute(root: TreeNode) -> int:
    raise NotImplementedError("TODO")


def max_path_sum(root: TreeNode) -> int:
    raise NotImplementedError("TODO")


def max_path_sum_iterative(root: TreeNode) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    t = build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1])
    print(render(t))
    print("root-to-leaf = 22:", root_to_leaf_paths(t, 22), "| brute:", root_to_leaf_paths_brute(t, 22))
    print("downward paths = 22:", count_downward_paths(t, 22), "| brute:", count_downward_brute(t, 22))
    for lst in ([-10, 9, 20, None, None, 15, 7], [1, 2, 3], [-3], [-2, -1, -5], [2, -1, -2]):
        r = build(lst)
        print(f"max path sum {lst!s:<28} -> {max_path_sum(r):>3}  brute {max_path_sum_brute(r):>3}")
    deep = chain([(-1) ** i * i for i in range(10_000)])   # 0, -1, 2, -3, ...
    print("10,000-node chain, iterative max path sum:", max_path_sum_iterative(deep))


if __name__ == "__main__":
    main()
