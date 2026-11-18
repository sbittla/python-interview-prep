"""
Exercise 01 — Comprehension Workout                         [Tier: ★ Core]
Chapter 23 · Pattern: list/dict/set comprehensions · Target time: 15 min

Problem
-------
Write four small functions, each a single comprehension (or two at most):

1. ``even_squares(nums)``   -> list of n*n for every even n, in input order.
2. ``word_lengths(words)``  -> dict mapping each word (lower-cased) to its length.
3. ``invert(mapping)``      -> dict mapping each value to the *sorted list* of keys that had it.
4. ``transpose(matrix)``    -> rows become columns for a rectangular list of lists.

Examples
--------
>>> even_squares([1, 2, 3, 4])
[4, 16]
>>> word_lengths(["Hi", "there"])
{'hi': 2, 'there': 5}
>>> invert({"a": 1, "b": 2, "c": 1})
{1: ['a', 'c'], 2: ['b']}
>>> transpose([[1, 2, 3], [4, 5, 6]])
[[1, 4], [2, 5], [3, 6]]

Constraints
-----------
- Inputs fit in memory; ``matrix`` is rectangular (may be empty).
- Use comprehensions, not explicit ``for`` + ``append`` loops.

Hints
-----
- A comprehension filter goes at the end: ``[expr for x in xs if cond]``.
- ``invert`` is easiest as: distinct values first, then a nested comprehension per value.
- ``transpose``: the outer loop runs over column indices, the inner over rows.

Approach ladder
---------------
1. Loop + append — clear but verbose; 4-6 lines per function.
2. Comprehension — same O(n) time, one expression, no mutable accumulator to get wrong.
3. ``invert`` one-pass — a ``defaultdict(list)`` loop is O(n) while the nested comprehension is
   O(n * distinct values); we show both and explain the trade-off (readability vs. scaling).

Follow-ups
----------
- When would you stop using a comprehension? (side effects, > 2 ``for`` clauses, try/except needed)
- Why does ``[[0] * 3] * 3`` create a broken grid while ``[[0] * 3 for _ in range(3)]`` does not?
"""
from __future__ import annotations

from collections import defaultdict


def even_squares(nums: list[int]) -> list[int]:
    return [n * n for n in nums if n % 2 == 0]


def word_lengths(words: list[str]) -> dict[str, int]:
    return {w.lower(): len(w) for w in words}


def invert(mapping: dict) -> dict:
    """Nested-comprehension version: O(n * distinct values)."""
    values = sorted(set(mapping.values()))
    return {v: sorted(k for k, val in mapping.items() if val == v) for v in values}


def invert_one_pass(mapping: dict) -> dict:
    """Linear version: one loop with a defaultdict, then sort each bucket."""
    buckets: defaultdict = defaultdict(list)
    for k, v in mapping.items():
        buckets[v].append(k)
    return {v: sorted(ks) for v, ks in sorted(buckets.items())}


def transpose(matrix: list[list]) -> list[list]:
    if not matrix:
        return []
    return [[row[c] for row in matrix] for c in range(len(matrix[0]))]


def main() -> None:
    print("even_squares:", even_squares([1, 2, 3, 4, 5, 6]))
    print("even_squares([]):", even_squares([]))
    print("word_lengths:", word_lengths(["Python", "is", "FUN"]))
    grades = {"ann": "A", "bob": "B", "cid": "A", "dee": "C", "eve": "B"}
    print("invert:", invert(grades))
    print("invert_one_pass:", invert_one_pass(grades))
    print("same result:", invert(grades) == invert_one_pass(grades))
    print("transpose:", transpose([[1, 2, 3], [4, 5, 6]]))
    print("transpose([]):", transpose([]))
    # The aliasing trap the follow-up asks about:
    bad = [[0] * 3] * 3
    bad[0][0] = 9
    good = [[0] * 3 for _ in range(3)]
    good[0][0] = 9
    print("bad grid :", bad)
    print("good grid:", good)
    # Set comprehension: distinct first letters, sorted for deterministic output.
    print("first letters:", sorted({w[0] for w in ["apple", "avocado", "banana", "cherry"]}))


if __name__ == "__main__":
    main()
