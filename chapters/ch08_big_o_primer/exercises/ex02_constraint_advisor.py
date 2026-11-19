"""
Exercise 02 — Constraint-to-Complexity Advisor              [Tier: ★ Core]
Chapter 08 · Pattern: read constraints before designing · Target time: 15 min

Problem
-------
Interview statements end with a constraints line such as
"1 <= nums.length <= 2 * 10^5". Write:

1. ``parse_bound(text)`` — return the largest integer upper bound in the text.
   Accept ``10^5``, ``10**5``, ``2 * 10^5``, ``1e5``, ``5000`` and ``5,000``.
2. ``max_complexity(n, python=False)`` — the slowest complexity class that is
   normally acceptable for input size n, from the two-column table ``TABLE``:

   class        classic rule (~10^8 ops)   CPython (~10^7 simple steps/s)
   O(n!)        n <= 10                    n <= 10
   O(2^n)       n <= 20                    n <= 18
   O(n^3)       n <= 500                   n <= 200
   O(n^2)       n <= 5,000                 n <= 3,000
   O(n log n)   n <= 10^6                  n <= 5 * 10^5
   O(n)         n <= 10^8                  n <= 10^7
   O(log n)     larger                     larger

   The classic column is the judge rule of thumb for compiled languages and
   rounds generously (500^3 = 1.25e8). Every CPython limit must stay within
   ``max_n(label, 10**7)``, i.e. about one second of plain Python.
3. ``estimated_ops(label, n)`` — g(n) for that class, as an int (log base 2,
   rounded up; O(2^n) counts n·2ⁿ since you touch each subset's n items).
4. ``max_n(label, budget)`` — the largest n whose estimate fits the budget.
5. ``slowest_feasible(n, budget)`` — the slowest class whose estimate fits.

Examples
--------
>>> parse_bound("1 <= nums.length <= 2 * 10^5")
200000
>>> max_complexity(200_000)
'O(n log n)'
>>> max_complexity(5_000), max_complexity(5_000, python=True)
('O(n^2)', 'O(n log n)')

Constraints
-----------
- n >= 1; ``parse_bound`` raises ValueError when no number is present.

Hints
-----
- One regex with alternatives: [a *] 10^k | 10**k | 1e5 | 5,000 | 5000.
- Walk TABLE in order and return the first row whose limit (classic or CPython) >= n.
- Compute only the formula you need: n! for n = 10^8 never finishes.
- max_n: gallop (double hi) then binary search; walk up one by one for 2^n and n!.
- slowest_feasible: try classes slowest-first and skip 2^n / n! for big n.

Follow-ups
----------
- Two inputs (n, m)? Estimate with both, e.g. O(n·m) for a grid.
- Many queries q over static data? Budget preprocessing + q · per-query cost.
"""
from __future__ import annotations

import math
import re  # noqa: F401  (you will likely need it)

# (classic max n, CPython max n, class, typical techniques)
TABLE: list[tuple[float, float, str, str]] = [
    (10, 10, "O(n!)", "all permutations, brute-force search"),
    (20, 18, "O(2^n)", "all subsets, bitmask DP"),
    (500, 200, "O(n^3)", "triple loops, interval DP, Floyd-Warshall"),
    (5_000, 3_000, "O(n^2)", "all pairs, 2-D DP"),
    (10**6, 5 * 10**5, "O(n log n)", "sort, heap, binary search per item"),
    (10**8, 10**7, "O(n)", "one pass: hashing, two pointers, prefix sums"),
    (math.inf, math.inf, "O(log n)", "math formula, binary search on the answer"),
]
PYTHON_STEPS = 10**7          # ~1 s of simple CPython steps
SLOWEST_FIRST = ["O(n!)", "O(2^n)", "O(n^3)", "O(n^2)", "O(n log n)", "O(n)", "O(log n)", "O(1)"]


def parse_bound(text: str) -> int:
    raise NotImplementedError("TODO")


def max_complexity(n: int, python: bool = False) -> str:
    raise NotImplementedError("TODO")


def techniques(label: str) -> str:
    return next(hint for _, _, lab, hint in TABLE if lab == label)


def estimated_ops(label: str, n: int) -> int:
    raise NotImplementedError("TODO")


def max_n(label: str, budget: int) -> int:
    """Largest n >= 1 with estimated_ops(label, n) <= budget (0 if none)."""
    raise NotImplementedError("TODO")


def slowest_feasible(n: int, budget: int = PYTHON_STEPS) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    for text in ["1 <= n <= 8", "1 <= nums.length <= 2 * 10^5", "n <= 5,000",
                 "0 <= k <= 1e9", "1 <= len(s) <= 10**4 and 1 <= q <= 100"]:
        n = parse_bound(text)
        classic, cpy = max_complexity(n), max_complexity(n, python=True)
        print(f"{text:<40} n={n:<13,} classic {classic:<10} CPython {cpy:<10} ({techniques(cpy)})")
    print("\nCPython column vs a 1e7-step budget:")
    for _, cpython, label, _ in TABLE[:-1]:
        n = int(cpython)
        exact = max_n(label, PYTHON_STEPS)
        print(f"  {label:<10} n<={n:<10,} ~{estimated_ops(label, n):.1e} steps  "
              f"exact max n={exact:<10,} within budget: {n <= exact}")
    print("slowest class within 1e7 steps at n=20:", slowest_feasible(20))


if __name__ == "__main__":
    main()
