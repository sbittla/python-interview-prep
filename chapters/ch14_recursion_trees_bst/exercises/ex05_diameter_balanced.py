"""
Exercise 05 — Height, Diameter and Balanced Check in One Pass     [Tier: ★ Core]
Chapter 14 · Pattern: return info up the tree (postorder) · Target time: 20 min

Problem
-------
For a binary tree compute
(a) height: number of nodes on the longest root-to-leaf path (empty tree: 0);
(b) diameter: number of EDGES on the longest path between any two nodes (the
    path need not pass through the root);
(c) balanced: True if, at every node, the heights of the two subtrees differ by
    at most 1.
Then compute diameter and balanced together in a single O(n) traversal.

Examples
--------
>>> diameter_and_balanced(build([1, 2, 3, 4, 5]))
(3, True)
>>> diameter_and_balanced(build([1, 2, None, 3]))
(2, False)

Constraints
-----------
- 0 <= n <= 10**5 (the iterative version must handle a chain of 10**5 nodes).

Hints
-----
- The longest path *through* a node has hl + hr edges (hl, hr = child heights).
- Return a tuple; avoid a module-level `best` variable (stale between calls).

Edge cases
----------
- Empty tree -> (0, True); single node -> (0, True); chain of 3 -> (2, False).

Wrong-but-tempting
------------------
- Diameter = height(left) + height(right) at the ROOT only: misses paths that stay
  inside one subtree ([1, 2, None, 3, 4, 5, None, 6]).
- Balanced = "root's subtrees differ by <= 1": must hold at EVERY node.
- A global accumulator that is never reset: correct once, wrong on the 2nd call.

Follow-ups
----------
- Early exit: return height -1 as a sentinel for "unbalanced" and stop combining.
- Diameter in a general graph tree: two BFS passes (→ §16.3).
"""
from __future__ import annotations

from collections import deque

from treenode import TreeNode, build, chain, render


def height(root: TreeNode | None) -> int:
    raise NotImplementedError("TODO")


def height_bfs(root: TreeNode | None) -> int:
    raise NotImplementedError("TODO")


def diameter_brute(root: TreeNode | None) -> int:
    raise NotImplementedError("TODO")


def balanced_brute(root: TreeNode | None) -> bool:
    raise NotImplementedError("TODO")


def diameter_and_balanced(root: TreeNode | None) -> tuple[int, bool]:
    raise NotImplementedError("TODO")


def diameter_and_balanced_iterative(root: TreeNode | None) -> tuple[int, bool]:
    raise NotImplementedError("TODO")


_best = 0  # deliberately WRONG pattern, kept to show the bug


def diameter_global_bug(root: TreeNode | None) -> int:
    def h(node: TreeNode | None) -> int:
        global _best
        if node is None:
            return 0
        lh, rh = h(node.left), h(node.right)
        _best = max(_best, lh + rh)
        return 1 + max(lh, rh)

    h(root)
    return _best                            # never reset: leaks into the next call


def main() -> None:
    root = build([1, 2, None, 3, 4, 5, None, 6])
    print(render(root))
    print("height:", height(root), height_bfs(root),
          "| diameter at root only:", height(root.left) + height(root.right))
    print("brute :", diameter_brute(root), balanced_brute(root))
    print("one pass:", diameter_and_balanced(root),
          "iterative:", diameter_and_balanced_iterative(root))
    for lst in ([], [1], [1, 2, 3, 4, 5], [1, 2, None, 3]):
        t = build(lst)
        print(f"{lst!s:<16} -> {diameter_and_balanced(t)}")
    long = chain(list(range(100_000)))
    print("chain of 100000, iterative:", diameter_and_balanced_iterative(long))
    print("global-variable version: big tree", diameter_global_bug(root),
          "then [1] ->", diameter_global_bug(build([1])), "(should be 0)")


if __name__ == "__main__":
    main()
