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

Approach ladder
---------------
1. Plain recursion — pick each key r as root: keys < r form the left subtree and
   keys > r the right, independently, so count(n) = sum over r of
   count(r - 1) * count(n - r). Correct but the same sub-counts are recomputed:
   5 * 3**(n-2) calls for n >= 2 (32,805 for n = 10): exponential.
2. Memoise — the answer depends only on n, so cache it (`functools.lru_cache`, or a
   dict). n + 1 distinct sub-problems, O(n) work each: O(n^2) time, O(n) space.
   The memo is the bridge to dynamic programming (top-down vs bottom-up, → §19.2).
3. Bottom-up table — fill count[0..n] in increasing order; no recursion at all.
   (The answers are the Catalan numbers.)

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
    if calls is not None:
        calls[0] += 1
    if n <= 1:
        return 1
    return sum(count_naive(r - 1, calls) * count_naive(n - r, calls) for r in range(1, n + 1))


@lru_cache(maxsize=None)
def count_memo(n: int) -> int:
    if n <= 1:
        return 1
    return sum(count_memo(r - 1) * count_memo(n - r) for r in range(1, n + 1))


def count_bottom_up(n: int) -> int:
    table = [1] * (n + 1)
    for size in range(2, n + 1):
        table[size] = sum(table[r - 1] * table[size - r] for r in range(1, size + 1))
    return table[n]


def generate(n: int) -> list[TreeNode | None]:
    def gen(lo: int, hi: int) -> list[TreeNode | None]:
        if lo > hi:
            return [None]                  # one way to build an empty subtree
        trees: list[TreeNode | None] = []
        for r in range(lo, hi + 1):
            for left in gen(lo, r - 1):
                for right in gen(r + 1, hi):
                    trees.append(TreeNode(r, left, right))
        return trees

    return gen(1, n) if n else [None]


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
