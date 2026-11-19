"""
Exercise 02 — How Many BST Shapes? (memoisation preview)          [Tier: ★ Core]
Chapter 14 · Pattern: recursion + memo (→ Ch 19) · Target time: 20 min

Problem
-------
(a) count(n): how many structurally different binary search trees hold the keys
    1..n? (n = 0 counts the empty tree: 1.)
(b) generate(n): return every one of those trees (as roots), for n <= 8.

Examples
--------
>>> count_memo(3)
5
>>> len(generate(3))
5

Constraints
-----------
- 0 <= n <= 19 for count (fits in 32 bits); 0 <= n <= 8 for generate.

Hints
-----
- Count how many times the plain function runs with a counter in a closure.
- generate(lo, hi): for each root r, combine every left tree from (lo, r-1) with
  every right tree from (r+1, hi). The empty range returns [None], not [].

Edge cases
----------
- n = 0 -> 1 tree (empty); n = 1 -> 1.

Wrong-but-tempting
------------------
- Returning [] for the empty range in generate: the product loop then yields
  nothing and every count becomes 0.
- Memoising generate and *sharing* subtree objects between trees is fine for
  reading, but mutating one returned tree then corrupts others.

Follow-ups
----------
- Why is the memo key just n and not (lo, hi)? (Only the size matters for counting.)
- Unbounded `lru_cache(maxsize=None)` on a method keeps `self` alive: a leak.
"""
from __future__ import annotations

from functools import lru_cache

from treenode import TreeNode


def count_naive(n: int, calls: list[int] | None = None) -> int:
    raise NotImplementedError("TODO")


@lru_cache(maxsize=None)
def count_memo(n: int) -> int:
    raise NotImplementedError("TODO")


def count_bottom_up(n: int) -> int:
    raise NotImplementedError("TODO")


def generate(n: int) -> list[TreeNode | None]:
    raise NotImplementedError("TODO")


def main() -> None:
    from treenode import render, to_level

    print("n :", [n for n in range(11)])
    print("count:", [count_memo(n) for n in range(11)])
    calls = [0]
    count_naive(10, calls)
    count_memo.cache_clear()
    count_memo(10)
    info = count_memo.cache_info()
    print(f"n=10 naive calls={calls[0]}  memo misses={info.misses} hits={info.hits}")
    print("bottom-up n=19:", count_bottom_up(19))
    trees = generate(3)
    print("generate(3):", [to_level(t) for t in trees])
    print(render(trees[2]))


if __name__ == "__main__":
    main()
