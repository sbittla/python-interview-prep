"""
Exercise 03 — Complexity Budget and Doubling Check          [Tier: ★ Core]
Chapter 02 · Pattern: interview method (state complexity) · Target time: 20 min

Problem
-------
State complexity twice: BEFORE coding (what the constraints allow) and AFTER
coding (what you actually wrote). Implement both checks.

1. feasible(n, ops_per_second=10**7, seconds=1.0) -> list of complexity class
   names whose operation count for size n fits in ops_per_second * seconds.
   Classes, cheapest first: "O(1)", "O(log n)", "O(n)", "O(n log n)",
   "O(n^2)", "O(n^3)", "O(2^n)", "O(n!)". The default 10**7 is a rough
   order-of-magnitude figure for simple CPython operations, not a measurement.

2. doubling_exponent(count_ops, n) -> float: run count_ops(n) and
   count_ops(2 * n), both returning an operation COUNT (not a time), and return
   log2(count(2n) / count(n)) rounded to 2 decimals. About 1 means linear,
   about 2 quadratic.

Examples
--------
>>> feasible(20)[-1]
'O(2^n)'
>>> feasible(10**6)[-1]
'O(n)'

Constraints
-----------
- n >= 1. Large n must not overflow or hang (do not compute 2**n for n = 10**9).
- Counting operations, not timing, keeps the result deterministic.

Hints
-----
- Compare in log2 space: log2(n^2) = 2*log2(n), log2(2^n) = n, and
  log2(n!) = lgamma(n + 1) / ln 2. Never build 2**n or n! for big n.
- For O(log n) and O(n log n) treat log2(n) < 1 as 1 so the cost is defined.
- doubling_exponent is one line: log2(count(2n) / count(n)), rounded.

Follow-ups
----------
- Two size parameters (n rows, m columns): budget O(n * m) vs O(n * m * log m).
- Why might a doubling test mislead? (Lower-order terms at small n; an
  input-dependent algorithm needs a worst-case generator.)
- In practice, time real runs at n and 2n with time.perf_counter (several
  repeats, take the minimum); counts are used here only for determinism.
"""
from __future__ import annotations

import math
from typing import Callable

CLASSES = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)", "O(n!)"]


def log2_cost(name: str, n: int) -> float:
    raise NotImplementedError("TODO")


def feasible(n: int, ops_per_second: float = 10**7, seconds: float = 1.0) -> list[str]:
    raise NotImplementedError("TODO")


def doubling_exponent(count_ops: Callable[[int], int], n: int) -> float:
    raise NotImplementedError("TODO")


# Two pair-counting loop structures, instrumented to count inner-loop steps.
# The step count depends only on n (not on the values), so no input data is needed.
def ops_brute(n: int) -> int:
    ops = 0
    for i in range(n):
        for _ in range(i + 1, n):
            ops += 1
    return ops


def ops_hash(n: int) -> int:
    seen: dict[int, int] = {}
    ops = 0
    for x in range(n):
        ops += 1
        seen[x % 10] = seen.get(x % 10, 0) + 1
    return ops


def main() -> None:
    print("Largest class that fits in ~1 s at 10^7 simple ops/s:")
    for n in [10, 20, 500, 3_000, 10**5, 10**6, 10**9]:
        print(f"  n = {n:>13,}: {feasible(n)[-1]}")
    print("\nDoubling check (operation counts, n = 1000 -> 2000):")
    print(f"  brute pair count exponent ~ {doubling_exponent(ops_brute, 1000)}")
    print(f"  hash  pair count exponent ~ {doubling_exponent(ops_hash, 1000)}")


if __name__ == "__main__":
    main()
