"""
Exercise 12 — defaultdict Phantom Keys, Counter Drops   [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (collections) · Target time: 10 min

Problem
-------
1. `count_hits(index, queries)` gets an inverted index `defaultdict(list)` mapping
   word -> list of document ids and returns how many queries have at least one
   hit. It must NOT modify `index`. The buggy version tests `if index[q]:`, and
   READING a missing key of a defaultdict inserts it (with an empty list).
2. `remaining_stock(stock, orders)` takes two Counters and returns a NEW Counter
   with `stock - orders` for EVERY product in either — including zero and negative
   results (negative = back-order). The buggy version uses the `-` operator,
   which silently drops every count <= 0.

Examples
--------
>>> idx = defaultdict(list, {"cat": [1, 3]})
>>> count_hits(idx, ["cat", "dog"]), sorted(idx)
(1, ['cat'])
>>> remaining_stock(Counter(apple=2, pear=1), Counter(apple=2, pear=3))
Counter({'apple': 0, 'pear': -2})

Constraints
-----------
- Inputs must not be mutated.

Approach ladder
---------------
1. Buggy  — `d[k]` on a defaultdict calls the factory and stores the result;
   `Counter.__sub__` keeps only positive counts.
2. Fixed  — use `k in d` or `d.get(k)` for read-only checks; use
   `Counter.subtract()` on a copy (it keeps zeros and negatives), adding missing
   order keys explicitly.

Follow-ups
----------
- Which Counter operations drop non-positive counts? (`+`, `-`, `&`, `|`, unary `+`.)
- How do you strip zero/negative counts on purpose? (`+c`.)
"""
from __future__ import annotations

from collections import Counter, defaultdict


def buggy_count_hits(index: defaultdict[str, list[int]], queries: list[str]) -> int:
    return sum(1 for q in queries if index[q])


def buggy_remaining_stock(stock: Counter[str], orders: Counter[str]) -> Counter[str]:
    return stock - orders


def count_hits(index: defaultdict[str, list[int]], queries: list[str]) -> int:
    """Read-only lookups: .get() never inserts into a defaultdict."""
    return sum(1 for q in queries if index.get(q))


def remaining_stock(stock: Counter[str], orders: Counter[str]) -> Counter[str]:
    """Keep zero and negative balances (Counter.subtract does)."""
    result = Counter(stock)          # copy: do not mutate the caller's Counter
    result.subtract(orders)          # missing keys start at 0 and go negative
    return result


def main() -> None:
    index: defaultdict[str, list[int]] = defaultdict(list, {"cat": [1, 3], "dog": [2]})
    print("buggy hits:", buggy_count_hits(index, ["cat", "cow", "emu"]),
          "| index keys after:", sorted(index))
    index = defaultdict(list, {"cat": [1, 3], "dog": [2]})
    print("fixed hits:", count_hits(index, ["cat", "cow", "emu"]),
          "| index keys after:", sorted(index))

    stock = Counter(apple=2, pear=1, plum=5)
    orders = Counter(apple=2, pear=3, kiwi=1)
    print("buggy remaining:", sorted(buggy_remaining_stock(stock, orders).items()))
    print("fixed remaining:", sorted(remaining_stock(stock, orders).items()))
    print("unary + strips <= 0:", sorted((+remaining_stock(stock, orders)).items()))


if __name__ == "__main__":
    main()
