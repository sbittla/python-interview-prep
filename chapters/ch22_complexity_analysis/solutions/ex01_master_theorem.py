"""
Exercise 01 — Master-Theorem Solver with Numeric Check     [Tier: ★ Core]
Chapter 22 · Pattern: divide-and-conquer recurrence · Target time: 25 min

Problem
-------
A divide-and-conquer algorithm on input size n makes ``a`` recursive calls on
inputs of size n/b and does f(n) = n^c * (log n)^k extra work:

    T(n) = a * T(n / b) + n^c * log^k n,      a >= 1, b > 1, c >= 0, k >= 0

Write ``master(a, b, c, k)`` returning ``(case, theta)`` where ``case`` is 1, 2
or 3 and ``theta`` is the tight bound as text, e.g. ``"n log n"``.

Then check the answer without trusting the theorem:

- ``evaluate(a, b, c, k, n)`` computes T(n) exactly for n a power of b, with
  T(1) = 1, by direct evaluation (all a sub-calls share the same argument, so
  T(n) = a * T(n/b) + f(n) needs only log_b n steps).
- ``level_costs(a, b, c, k, n)`` returns the work on each level of the
  recursion tree: level i has a^i nodes of size n/b^i.
- ``ratio_spread(a, b, c, k)`` returns max/min of T(n)/g(n) over
  n = b^8 ... b^16, where g is the claimed bound; a value near 1 (we accept
  < 2.5) means the bound is tight up to a constant.

Examples
--------
>>> master(2, 2, 1, 0)
(2, 'n log n')
>>> master(3, 2, 1, 0)
(1, 'n^1.585')
>>> master(2, 2, 2, 0)
(3, 'n^2')

Constraints
-----------
- a >= 1, b >= 2 integers; c >= 0, k a non-negative integer.

Approach ladder
---------------
1. Unroll by hand — expand T(n) a few levels, guess the pattern. Works, but
   slow and error-prone in an interview; O(log n) levels to sum.
2. Recursion tree — level i costs a^i * f(n/b^i). If level costs grow
   geometrically the leaves dominate (n^(log_b a) leaves); if they are equal
   every one of the log_b n levels counts; if they shrink the root dominates.
3. Master theorem — compare c with the critical exponent e = log_b a:
   case 1  c < e            -> Θ(n^e)
   case 2  c = e (k >= 0)   -> Θ(n^e log^(k+1) n)
   case 3  c > e            -> Θ(n^c log^k n), needs regularity
           a*f(n/b) <= δ f(n) for some δ < 1 and large n; for f = n^c log^k n
           with c > e it always holds (a / b^c < 1).
   O(1) to apply; we keep rung 2 as the numeric check.

Follow-ups
----------
- f(n) = n / log n with a = b = 2 (k = -1) falls between cases 2 and 3 of the
  basic theorem; the extended version gives Θ(n log log n). This solver
  rejects k < 0.
- T(n) = T(n-1) + T(n-2) + 1 (naive Fibonacci) shrinks by subtraction, not
  division: not Master form. See ex04 for its exact call count.
- *Closest pair of points that re-sorts the strip at every level.
- Akra–Bazzi handles unequal splits such as T(n) = T(n/3) + T(2n/3) + n.
"""
from __future__ import annotations

import math
from functools import lru_cache


def _critical_exponent(a: int, b: int) -> float:
    return math.log(a) / math.log(b)


def _fmt_exp(x: float) -> str:
    r = round(x)
    return str(r) if math.isclose(x, r, abs_tol=1e-9) else f"{x:.3f}"


def _fmt_power(e: float) -> str:
    if math.isclose(e, 0, abs_tol=1e-9):
        return ""
    if math.isclose(e, 1, abs_tol=1e-9):
        return "n"
    return f"n^{_fmt_exp(e)}"


def _fmt_log(k: int) -> str:
    return "" if k == 0 else ("log n" if k == 1 else f"log^{k} n")


def master(a: int, b: int, c: float, k: int = 0) -> tuple[int, str]:
    if a < 1 or b < 2 or c < 0:
        raise ValueError("need a >= 1, b >= 2, c >= 0")
    if k < 0 or k != int(k):
        raise ValueError("this solver handles f(n) = n^c log^k n with integer k >= 0")
    e = _critical_exponent(a, b)
    if math.isclose(c, e, abs_tol=1e-9):
        case, power, logs = 2, e, k + 1
    elif c < e:
        case, power, logs = 1, e, 0
    else:
        case, power, logs = 3, c, k
    text = " ".join(p for p in (_fmt_power(power), _fmt_log(logs)) if p) or "1"
    return case, text


def _f(c: float, k: int, n: int) -> float:
    return n ** c * (math.log2(n) ** k if k else 1.0)


def evaluate(a: int, b: int, c: float, k: int, n: int) -> float:
    """Exact T(n) for n = b^j by direct evaluation; T(1) = 1."""

    @lru_cache(maxsize=None)
    def t(m: int) -> float:
        if m <= 1:
            return 1.0
        return a * t(m // b) + _f(c, k, m)

    return t(n)


def level_costs(a: int, b: int, c: float, k: int, n: int) -> list[float]:
    """Work on each level of the recursion tree, root first, leaves last."""
    costs, nodes, size = [], 1, n
    while size > 1:
        costs.append(nodes * _f(c, k, size))
        nodes, size = nodes * a, size // b
    costs.append(float(nodes))                      # leaves: T(1) = 1 each
    return costs


def bound(a: int, b: int, c: float, k: int, n: int) -> float:
    """The claimed Θ-function g(n) evaluated numerically."""
    case = master(a, b, c, k)[0]
    e = _critical_exponent(a, b)
    lg = math.log2(n)
    if case == 1:
        return n ** e
    if case == 2:
        return n ** e * lg ** (k + 1)
    return n ** c * lg ** k


def ratio_spread(a: int, b: int, c: float, k: int, g=None) -> float:
    """max/min of T(n)/g(n) over n = b^8..b^16; g defaults to the claimed bound."""
    g = g or (lambda n: bound(a, b, c, k, n))
    ratios = [evaluate(a, b, c, k, b ** j) / g(b ** j) for j in range(8, 17)]
    return max(ratios) / min(ratios)


def recurrence_text(a: int, b: int, c: float, k: int) -> str:
    f = " ".join(p for p in (_fmt_power(c), _fmt_log(k)) if p) or "1"
    return f"{a if a > 1 else ''}T(n/{b}) + {f}"


EXAMPLES = [
    ("binary search", 1, 2, 0, 0),
    ("merge sort", 2, 2, 1, 0),
    ("Karatsuba", 3, 2, 1, 0),
    ("Strassen", 7, 2, 2, 0),
    ("closest pair*", 2, 2, 1, 1),
    ("root-heavy", 2, 2, 2, 0),
]


def main() -> None:
    for name, a, b, c, k in EXAMPLES:
        case, theta = master(a, b, c, k)
        spread = ratio_spread(a, b, c, k)
        print(f"{name:17} T(n) = {recurrence_text(a, b, c, k):18} case {case}"
              f"  {'Theta(' + theta + ')':16} tight: {spread < 2.5}")
    print()
    for name, a, b, c, k in [("leaf-heavy (Karatsuba)", 3, 2, 1, 0),
                             ("balanced (merge sort)", 2, 2, 1, 0),
                             ("root-heavy", 2, 2, 2, 0)]:
        costs = level_costs(a, b, c, k, 2 ** 10)
        print(f"{name:23} last level / root level = {costs[-1] / costs[0]:.3g}")
    wrong = ratio_spread(3, 2, 1, 0, g=lambda n: n * math.log2(n))
    print(f"Karatsuba claimed as n log n -> tight: {wrong < 2.5}")
    for bad in [(2, 2, 1, -1), (1, 1, 0, 0)]:
        try:
            master(*bad)
        except ValueError as exc:
            print(f"master{bad}: ValueError: {exc}")


if __name__ == "__main__":
    main()
