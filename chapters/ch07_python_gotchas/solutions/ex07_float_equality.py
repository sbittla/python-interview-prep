"""
Exercise 07 — Bills That Never Settle                   [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (numbers) · Target time: 8 min

Problem
-------
1. `is_settled(payments, total)` returns True when the float payments add up to
   the total. The buggy version uses `sum(payments) == total`, which fails for
   `[0.1, 0.2]` vs `0.3` because binary floats cannot represent 0.1 exactly.
2. `exact_total(prices)` receives prices as strings ("0.10") and must return the
   exact sum as a string with the natural number of decimal places ("0.30").
   The buggy version converts to float and returns "0.30000000000000004".

Examples
--------
>>> is_settled([0.1, 0.2], 0.3)
True
>>> exact_total(["0.10", "0.20"])
'0.30'

Constraints
-----------
- Money amounts are at most a few million with <= 2 decimal places.

Approach ladder
---------------
1. Buggy  — `==` on floats; float arithmetic for money.
2. Fixed  — compare with `math.isclose(a, b, abs_tol=1e-9)` (always give abs_tol
   when the expected value may be 0); do money in `decimal.Decimal` built from
   STRINGS (Decimal(0.1) inherits the float error) — or in integer cents.

Follow-ups
----------
- Why is `math.isclose(x, 0.0)` False for x = 1e-17 without abs_tol?
- When would you use `fractions.Fraction`? (Exact rational arithmetic, e.g. 1/3.)
"""
from __future__ import annotations

import math
from decimal import Decimal


def buggy_is_settled(payments: list[float], total: float) -> bool:
    return sum(payments) == total


def buggy_exact_total(prices: list[str]) -> str:
    return str(sum(float(p) for p in prices))


def is_settled(payments: list[float], total: float) -> bool:
    """True if the payments add up to total within a tiny tolerance."""
    return math.isclose(math.fsum(payments), total, rel_tol=1e-9, abs_tol=1e-9)


def exact_total(prices: list[str]) -> str:
    """Exact decimal sum of price strings."""
    return str(sum((Decimal(p) for p in prices), Decimal("0")))


def main() -> None:
    print("0.1 + 0.2 =", 0.1 + 0.2)
    print("buggy is_settled:", buggy_is_settled([0.1, 0.2], 0.3))
    print("fixed is_settled:", is_settled([0.1, 0.2], 0.3))
    print("fixed is_settled (short):", is_settled([0.1, 0.2], 0.31))
    print("buggy exact_total:", buggy_exact_total(["0.10", "0.20"]))
    print("fixed exact_total:", exact_total(["0.10", "0.20"]))
    print("Decimal from float:", Decimal(0.1))


if __name__ == "__main__":
    main()
