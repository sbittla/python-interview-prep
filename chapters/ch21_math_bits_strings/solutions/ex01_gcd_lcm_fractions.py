"""
Exercise 01 — GCD / LCM of a List and Fraction Reduction       [Tier: ★ Core]
Chapter 21 · Pattern: Euclid's algorithm · Target time: 15 min

Problem
-------
1. ``gcd_euclid(a, b)``: greatest common divisor of two integers (either may be negative or
   zero; ``gcd(0, 0) == 0``; the result is never negative).
2. ``gcd_list(nums)`` / ``lcm_list(nums)``: GCD and LCM of a list. Empty list: GCD 0, LCM 1
   (the identities, matching ``math.gcd()`` and ``math.lcm()``). Any zero makes the LCM 0.
3. ``reduce_fraction(num, den)``: lowest terms with a positive denominator. ``den == 0``
   raises ``ZeroDivisionError``.

Examples
--------
>>> gcd_euclid(48, 18), gcd_euclid(-4, 6), gcd_euclid(0, 0)
(6, 2, 0)
>>> gcd_list([12, 18, 30]), lcm_list([4, 6, 10])
(6, 60)
>>> reduce_fraction(6, -8)
(-3, 4)

Constraints
-----------
- Python ints are unbounded, so ``a * b`` never overflows; still compute
  ``a // gcd(a, b) * b`` to keep intermediates small.

Approach ladder
---------------
1. Brute force — try every d from min(|a|, |b|) down to 1. O(min(|a|, |b|)) time, O(1) space:
   hopeless for 10**18.
2. Optimal    — Euclid: gcd(a, b) = gcd(b, a mod b). O(log min(|a|, |b|)) iterations (Lamé),
   O(1) space. A list folds pairwise: O(n log M) for values up to M.
3. Stdlib     — ``math.gcd(*nums)`` and ``math.lcm(*nums)`` (both variadic since 3.9).
   Why move up: the brute force is linear in the value, Euclid is logarithmic.

Follow-ups
----------
- Extended Euclid returns x, y with a*x + b*y = gcd(a, b) -> modular inverse (ex03).
- Do all fractions in a list reduce to the same value? Compare reduced (num, den) tuples.
- ``fractions.Fraction`` does all of this; show it as the production answer.
"""
from __future__ import annotations

import math
from fractions import Fraction
from functools import reduce


def gcd_brute(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    if a == 0 or b == 0:
        return a or b                  # gcd(0, b) = |b|
    for d in range(min(a, b), 0, -1):
        if a % d == 0 and b % d == 0:
            return d
    return 1                           # unreachable: d = 1 always divides


def gcd_euclid(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)                      # sign of % follows b; abs fixes negatives


def gcd_list(nums: list[int]) -> int:
    return reduce(gcd_euclid, nums, 0)          # gcd(0, x) = |x|


def lcm_list(nums: list[int]) -> int:
    def lcm2(a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        return abs(a // gcd_euclid(a, b) * b)   # divide first: smaller intermediate
    return reduce(lcm2, nums, 1)


def reduce_fraction(num: int, den: int) -> tuple[int, int]:
    if den == 0:
        raise ZeroDivisionError("denominator is zero")
    g = gcd_euclid(num, den)           # g >= 1 because den != 0
    num, den = num // g, den // g
    if den < 0:
        num, den = -num, -den
    return num, den


def main() -> None:
    for a, b in [(48, 18), (-4, 6), (4, -6), (0, 7), (0, 0), (17, 5)]:
        print(f"gcd({a}, {b}) = {gcd_euclid(a, b)}  brute={gcd_brute(a, b)}  "
              f"math={math.gcd(a, b)}")
    for nums in [[12, 18, 30], [4, 6, 10], [7], [], [0, 5], [-4, 6]]:
        print(f"nums={nums!s:<12} gcd={gcd_list(nums):<3} lcm={lcm_list(nums):<3} "
              f"math: gcd={math.gcd(*nums)} lcm={math.lcm(*nums)}")
    for n, d in [(6, -8), (-6, -8), (0, 5), (10, 4)]:
        f = Fraction(n, d)
        print(f"{n}/{d} -> {reduce_fraction(n, d)}  Fraction={f.numerator}/{f.denominator}")
    try:
        reduce_fraction(1, 0)
    except ZeroDivisionError as e:
        print("reduce_fraction(1, 0) ->", type(e).__name__)


if __name__ == "__main__":
    main()
