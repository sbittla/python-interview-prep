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

Approach ladder
---------------
1. Brute force — read the code and guess. Slices and list comprehensions
   look free.
2. Improved   — `sys.getsizeof` on the result. Shallow and after the fact:
   it misses temporaries that were built and thrown away.
3. Optimal    — tracemalloc peak while the code runs: captures temporaries.
   Generator: O(1) extra memory instead of O(n). memoryview slice: O(1)
   view instead of an O(k) copy. Index loop: O(1) instead of O(n) per step
   (the slice loop is also O(n^2) time).

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
    tracemalloc.start()
    try:
        fn()
        return tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()


def squares_list(n: int) -> int:
    return sum([i * i for i in range(n)])


def squares_gen(n: int) -> int:
    return sum(i * i for i in range(n))


def checksum_bytes(data: bytes, k: int) -> int:
    return sum(data[i:i + k][0] for i in range(0, len(data), k))


def checksum_view(data: bytes, k: int) -> int:
    view = memoryview(data)
    return sum(view[i:i + k][0] for i in range(0, len(data), k))


def drain_slices(xs: list[int]) -> int:
    total = 0
    while xs:
        total += xs[0]
        xs = xs[1:]                     # O(n) copy every step
    return total


def drain_index(xs: list[int]) -> int:
    total = 0
    for i in range(len(xs)):
        total += xs[i]
    return total


def report(n: int) -> dict[str, tuple[bool, bool]]:
    data = bytes(range(256)) * (n // 64)
    xs = list(range(n // 10))
    pairs = {
        "generator vs list": (lambda: squares_list(n), lambda: squares_gen(n)),
        "memoryview vs bytes slice": (lambda: checksum_bytes(data, 4096),
                                      lambda: checksum_view(data, 4096)),
        "index vs slice loop": (lambda: drain_slices(xs), lambda: drain_index(xs)),
    }
    out = {}
    for label, (heavy, lean) in pairs.items():
        out[label] = (heavy() == lean(), peak(lean) < peak(heavy))
    return out


def overallocation() -> dict[str, bool]:
    grown: list[int] = []
    sizes = set()
    for i in range(1000):
        grown.append(i)
        sizes.add(sys.getsizeof(grown))
    small: list[int] = []
    for i in range(10):
        small.append(i)
    return {
        "append-built list is larger than list(range)":
            sys.getsizeof(small) > sys.getsizeof(list(range(10))),
        "resizes are rare": len(sizes) < 50,
    }


def main() -> None:
    for label, (same, lean_wins) in report(200_000).items():
        print(f"{label:26} same result: {same}  lean peak lower: {lean_wins}")
    for claim, ok in overallocation().items():
        print(f"{claim}: {ok}")


if __name__ == "__main__":
    main()
