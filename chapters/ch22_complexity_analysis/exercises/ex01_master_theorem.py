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
  < TIGHT = 1.3) means the bound is tight up to a constant. Keep the
  threshold low: a missing log factor only moves the ratio about 2x over
  this range (log n goes from 8 to 16 when b = 2).

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

Hints
-----
- Critical exponent e = log_b a (helper provided). Compare c with e using
  math.isclose, not ==, because log_b a is a float.
- Format the answer with the provided _fmt_power / _fmt_log helpers.
- evaluate: memoise t(m) = a * t(m // b) + f(m); only log_b n distinct
  arguments ever occur.
- level_costs: level i has a^i nodes of size n / b^i; the last entry is the
  leaf level, a^depth nodes costing T(1) = 1 each.

Follow-ups
----------
- f(n) = n / log n with a = b = 2 (k = -1) falls between cases 1 and 2 of the
  basic theorem: it is o(n) but not O(n^(1-ε)) for any ε > 0. The extended
  version gives Θ(n log log n). This solver rejects k < 0.
- Gap between cases 2 and 3: under the basic (k = 0 only) theorem,
  2T(n/2) + n log n fits neither; the extended case 2 gives Θ(n log^2 n).
- n not a power of b: floors and ceilings (T(⌊n/b⌋), T(⌈n/b⌉)) do not change
  the Θ bound.
- T(n) = T(n-1) + T(n-2) + 1 (naive Fibonacci) shrinks by subtraction, not
  division: not Master form. See ex04 for its exact call count.
- *Closest pair of points that re-sorts the strip at every level.
- Akra–Bazzi handles unequal splits such as T(n) = T(n/3) + T(2n/3) + n.
"""
from __future__ import annotations

import math


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
    raise NotImplementedError("TODO")


def _f(c: float, k: int, n: int) -> float:
    return n ** c * (math.log2(n) ** k if k else 1.0)


def evaluate(a: int, b: int, c: float, k: int, n: int) -> float:
    """Exact T(n) for n = b^j by direct evaluation; T(1) = 1."""

    raise NotImplementedError("TODO")


def level_costs(a: int, b: int, c: float, k: int, n: int) -> list[float]:
    """Work on each level of the recursion tree, root first, leaves last."""
    raise NotImplementedError("TODO")


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


TIGHT = 1.3          # max/min ratio accepted as "constant"


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
              f"  {'Theta(' + theta + ')':16} tight: {spread < TIGHT}")
    print()
    for name, a, b, c, k in [("leaf-heavy (Karatsuba)", 3, 2, 1, 0),
                             ("balanced (merge sort)", 2, 2, 1, 0),
                             ("root-heavy", 2, 2, 2, 0)]:
        costs = level_costs(a, b, c, k, 2 ** 10)
        print(f"{name:23} last level / root level = {costs[-1] / costs[0]:.3g}")
    for label, a, g in [("Karatsuba claimed as n log n", 3, lambda n: n * math.log2(n)),
                        ("merge sort claimed as n", 2, lambda n: n)]:
        wrong = ratio_spread(a, 2, 1, 0, g=g)
        print(f"{label:28} -> tight: {wrong < TIGHT}  (spread {wrong:.2f})")
    for bad in [(2, 2, 1, -1), (1, 1, 0, 0)]:
        try:
            master(*bad)
        except ValueError as exc:
            print(f"master{bad}: ValueError: {exc}")


if __name__ == "__main__":
    main()
