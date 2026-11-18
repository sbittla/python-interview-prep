"""
Exercise 08 — Rounding and Negative Division            [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (numbers) · Target time: 10 min

Problem
-------
1. `round_half_up(value, places)` takes a decimal STRING and must round halves
   away from zero, as on a shop receipt: "2.5" -> 3, "0.125" at 2 places -> 0.13,
   "-2.5" -> -3. The buggy version uses `round(float(value), places)`, which uses
   banker's rounding (round-half-to-even) and float representation.
2. `div_toward_zero(a, b)` must divide integers and truncate toward zero, the way
   C, Java and many judges' reference solutions do: -7 / 2 -> -3. The buggy
   version uses `a // b`, which FLOORS (toward minus infinity): -7 // 2 == -4.

Examples
--------
>>> round_half_up("2.5", 0), round_half_up("0.125", 2)
(Decimal('3'), Decimal('0.13'))
>>> div_toward_zero(-7, 2), div_toward_zero(7, -2), div_toward_zero(7, 2)
(-3, -3, 3)

Constraints
-----------
- `b != 0`; |a|, |b| may be huge (Python ints are unbounded) — so do not go via float.

Approach ladder
---------------
1. Buggy  — `round()` is round-half-even; `//` floors; `%` takes the sign of the divisor.
2. Fixed  — `Decimal(value).quantize(Decimal(1).scaleb(-places), ROUND_HALF_UP)`;
   truncating division via `q = abs(a) // abs(b)` with the sign restored.
   (`int(a / b)` looks right but goes through float and breaks above 2**53.)

Follow-ups
----------
- What is `-7 % 3` in Python and why? (2: a == (a // b) * b + a % b always holds.)
- What does `math.fmod(-7, 3)` return? (-1.0 — C-style remainder.)
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def buggy_round_half_up(value: str, places: int = 0) -> Decimal:
    return Decimal(str(round(float(value), places)))


def buggy_div_toward_zero(a: int, b: int) -> int:
    return a // b


def round_half_up(value: str, places: int = 0) -> Decimal:
    """Round a decimal string half away from zero to `places` decimal places."""
    step = Decimal(1).scaleb(-places)          # places=2 -> Decimal('0.01')
    return Decimal(value).quantize(step, rounding=ROUND_HALF_UP)


def div_toward_zero(a: int, b: int) -> int:
    """Integer division truncated toward zero, exact for arbitrarily large ints."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q


def main() -> None:
    print("round(0.5), round(1.5), round(2.5):", round(0.5), round(1.5), round(2.5))
    for v, p in [("2.5", 0), ("0.125", 2), ("-2.5", 0), ("2.675", 2)]:
        print(f"round_half_up({v!r}, {p}): buggy={buggy_round_half_up(v, p)} "
              f"fixed={round_half_up(v, p)}")
    for a, b in [(-7, 2), (7, -2), (7, 2), (-6, 3)]:
        print(f"div_toward_zero({a}, {b}): buggy={buggy_div_toward_zero(a, b)} "
              f"fixed={div_toward_zero(a, b)}")
    big = 10**20 + 1
    print("int(-big / 1) == -big:", int(-big / 1) == -big)
    print("div_toward_zero(-big, 1) == -big:", div_toward_zero(-big, 1) == -big)


if __name__ == "__main__":
    main()
