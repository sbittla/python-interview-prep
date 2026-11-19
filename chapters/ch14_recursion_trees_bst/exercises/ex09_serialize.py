"""
Exercise 09 — Serialize and Deserialize a Binary Tree             [Tier: ◆ Extended]
Chapter 14 · Pattern: preorder with null markers; BFS · Target time: 25 min

Problem
-------
Design serialize(root) -> str and deserialize(s) -> root so that
deserialize(serialize(t)) has the same shape and values as t, for any binary
tree of ints (negative, multi-digit, repeated values allowed). Provide a
preorder (DFS) codec and a level-order (BFS) codec.

Examples
--------
>>> serialize(build([1, 2, 3, None, None, 4, 5]))
'1,2,#,#,3,4,#,#,5,#,#'
>>> to_level(deserialize('1,2,#,#,3,4,#,#,5,#,#'))
[1, 2, 3, None, None, 4, 5]
>>> serialize_bfs(build([1, 2, 3, None, None, 4, 5]))
'1,2,3,#,#,4,5'

Constraints
-----------
- 0 <= n <= 10**4. The BFS codec must also handle a 10**5-node chain.

Hints
-----
- Deserialize: `vals = iter(s.split(','))`; a helper takes next(vals); '#' -> None,
  otherwise build the node, then its left from the iterator, then its right.
- The empty tree must round-trip: serialize(None) == '#' (DFS) or '' (BFS).

Edge cases
----------
- Empty tree; single node; negative and multi-digit values; deep chain.

Wrong-but-tempting
------------------
- Preorder without null markers: [1, 2] (2 on the left) and [1, None, 2] (2 on the
  right) both give '1,2'.
- Concatenating digits with no separator: '1,23' and '12,3' collide as '123'.
- Using str(list) and eval(): unsafe and slow; split on a delimiter instead.

Follow-ups
----------
- BST only: preorder without markers is enough (keys fix the shape) -> more compact.
- Binary format: struct-pack values with a presence bitmap.
"""
from __future__ import annotations

from collections import deque

from treenode import TreeNode, build, chain, render, to_level


def serialize(root: TreeNode | None) -> str:
    raise NotImplementedError("TODO")


def deserialize(data: str) -> TreeNode | None:
    raise NotImplementedError("TODO")


def serialize_bfs(root: TreeNode | None) -> str:
    raise NotImplementedError("TODO")


def deserialize_bfs(data: str) -> TreeNode | None:
    raise NotImplementedError("TODO")


def preorder_no_markers(root: TreeNode | None) -> str:
    """The ambiguous format, kept to demonstrate the bug."""
    return ",".join(s for s in serialize(root).split(",") if s != "#")


def main() -> None:
    t = build([1, 2, 3, None, None, 4, 5])
    print(render(t))
    s = serialize(t)
    print("dfs:", s, "->", to_level(deserialize(s)))
    b = serialize_bfs(t)
    print("bfs:", b, "->", to_level(deserialize_bfs(b)))
    for lst in ([], [-7], [10, -20, None, 300], [1, 1, 1]):
        r = build(lst)
        print(f"{lst!s:<20} dfs={serialize(r)!r:<22} bfs={serialize_bfs(r)!r:<16}"
              f" ok={to_level(deserialize(serialize(r))) == lst == to_level(deserialize_bfs(serialize_bfs(r)))}")
    print("no markers:", preorder_no_markers(build([1, 2])), "vs",
          preorder_no_markers(build([1, None, 2])), "-> ambiguous")
    long = chain(list(range(100_000)))
    back = deserialize_bfs(serialize_bfs(long))
    print("bfs codec on 100000-node chain round-trips:",
          serialize_bfs(back) == serialize_bfs(long))


if __name__ == "__main__":
    main()
