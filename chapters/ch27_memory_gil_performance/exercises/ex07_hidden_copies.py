"""
Exercise 07 — Hidden Copies: Prove Them with tracemalloc     [Tier: ★ Core]
Chapter 27 · Pattern: comparative peak-memory measurement · Target time: 25 min

Problem
-------
Some lines copy data without saying so. Measure three pairs with
tracemalloc and report which variant has the lower peak.

1. `peak(fn)` returns the peak traced bytes while `fn()` runs (it starts and
   stops tracemalloc itself).
2. The pairs, each returning the same answer both ways:
     sum of squares       list comprehension  vs  generator expression
     checksum of chunks   bytes slicing data[i:i+k]  vs  memoryview slicing
     tail recursion-free  `rest = xs[1:]` loop  vs  an index loop
3. `report(n)` returns {label: (same_result, lean_variant_has_lower_peak)}.
4. `overallocation()` returns a dict of booleans about list growth:
     "append-built list is larger than list(range)"  over-allocation
     "resizes are rare"   distinct getsizeof values while appending 1,000
                          items < 50 (amortised O(1) append, → §22.3)

Examples
--------
>>> all(ok for ok in report(10_000).values())
True

Constraints
-----------
- Print booleans, never byte counts (they vary by version and platform).


Hints
-----
- `memoryview(data)[i:i+k]` shares the buffer; `bytes(view)` would copy.
- `tracemalloc.get_traced_memory()` returns (current, peak).

Follow-ups
----------
- Is `xs[:]` a copy? (Yes, shallow, O(n).) Is `xs[::-1]`? (Yes; use
  `reversed(xs)` for an O(1) iterator.)
- `zip`, `map`, `range`, `dict.items()` in Python 3 are lazy; in Python 2
  they built lists — a classic interview gotcha.
"""
from __future__ import annotations

import sys
import tracemalloc
from typing import Callable


def peak(fn: Callable[[], object]) -> int:
    raise NotImplementedError("TODO")


def squares_list(n: int) -> int:
    return sum([i * i for i in range(n)])


def squares_gen(n: int) -> int:
    raise NotImplementedError("TODO")


def checksum_bytes(data: bytes, k: int) -> int:
    return sum(data[i:i + k][0] for i in range(0, len(data), k))


def checksum_view(data: bytes, k: int) -> int:
    raise NotImplementedError("TODO")


def drain_slices(xs: list[int]) -> int:
    total = 0
    while xs:
        total += xs[0]
        xs = xs[1:]                     # O(n) copy every step
    return total


def drain_index(xs: list[int]) -> int:
    raise NotImplementedError("TODO")


def report(n: int) -> dict[str, tuple[bool, bool]]:
    raise NotImplementedError("TODO")


def overallocation() -> dict[str, bool]:
    raise NotImplementedError("TODO")


def main() -> None:
    for label, (same, lean_wins) in report(200_000).items():
        print(f"{label:26} same result: {same}  lean peak lower: {lean_wins}")
    for claim, ok in overallocation().items():
        print(f"{claim}: {ok}")


if __name__ == "__main__":
    main()
