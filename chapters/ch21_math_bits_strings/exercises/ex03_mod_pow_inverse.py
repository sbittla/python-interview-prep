"""
Exercise 03 — Fast Modular Power and Modular Inverse           [Tier: ★ Core]
Chapter 21 · Pattern: binary exponentiation, extended Euclid · Target time: 20 min

Problem
-------
1. ``mod_pow(a, b, m)``: a**b mod m for b >= 0 and m >= 1 without building a**b.
   ``a`` may be negative; the result is in [0, m). Raise ``ValueError`` for b < 0 or m < 1
   (every rung does the same).
2. ``ext_gcd(a, b)``: (g, x, y) with a*x + b*y == g == gcd(a, b).
3. ``mod_inverse(a, m)``: x in [0, m) with a*x ≡ 1 (mod m); ``ValueError`` when
   gcd(a, m) != 1 (as ``pow(a, -1, m)`` does).

Examples
--------
>>> mod_pow(3, 200, 13), pow(3, 200, 13)
(9, 9)
>>> mod_inverse(3, 11), pow(3, -1, 11)
(4, 4)

Constraints
-----------
- 0 <= b <= 10**18; 1 <= m <= 10**18.

Hints
-----
- Read b in binary: keep ``a, a^2, a^4, ...`` and multiply into the result when the bit is 1.
- Reduce after *every* multiplication so numbers never grow past m**2.
- Extended Euclid: carry (x, y) coefficients alongside the remainders.
- The inverse exists iff gcd(a, m) == 1; return x % m to land in [0, m).

Wrong-but-tempting
------------------
- ``a ** b % m``: builds a number with about b * log2(a) bits first.
- ``result = 1`` instead of ``1 % m``: wrong for m == 1.
- Fermat ``pow(a, m - 2, m)`` for a non-prime m: silently wrong.
- Fermat when p divides a: ``pow(a, p - 2, p)`` silently returns 0 instead of raising.

Follow-ups
----------
- Matrix fast power for Fibonacci in O(log n).
- Why ``m == 1`` returns 0: every integer is ≡ 0 (mod 1); pow(0, 0, 1) == 0 too.
"""
from __future__ import annotations


def _check(b: int, m: int) -> None:
    if b < 0:
        raise ValueError("exponent must be >= 0")
    if m < 1:
        raise ValueError("modulus must be >= 1")


def mod_pow_naive(a: int, b: int, m: int) -> int:
    raise NotImplementedError("TODO")


def mod_pow_recursive(a: int, b: int, m: int) -> int:
    raise NotImplementedError("TODO")


def mod_pow(a: int, b: int, m: int) -> int:
    raise NotImplementedError("TODO")


def ext_gcd(a: int, b: int) -> tuple[int, int, int]:
    raise NotImplementedError("TODO")


def mod_inverse(a: int, m: int) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    for a, b, m in [(3, 200, 13), (2, 10, 1000), (-2, 3, 5), (0, 0, 7), (5, 0, 1), (7, 10**18, 10**9 + 7)]:
        naive = mod_pow_naive(a, b, m) if b <= 1000 else "skipped"
        print(f"pow({a}, {b}, {m}) = {mod_pow(a, b, m)}  recursive={mod_pow_recursive(a, b, m)}"
              f"  naive={naive}  builtin={pow(a, b, m)}")
    for a, b in [(240, 46), (3, 11), (-7, 3)]:
        g, x, y = ext_gcd(a, b)
        print(f"ext_gcd({a}, {b}) = {(g, x, y)}  check {a}*{x} + {b}*{y} = {a * x + b * y}")
    for a, m in [(3, 11), (10, 17), (-3, 11), (6, 9)]:
        try:
            mine = mod_inverse(a, m)
        except ValueError as e:
            mine = f"ValueError({e})"
        try:
            builtin = pow(a, -1, m)
        except ValueError:
            builtin = "ValueError"
        print(f"inverse of {a} mod {m}: {mine}  builtin={builtin}")
    p = 10**9 + 7
    print("Fermat inverse of 2 mod 1e9+7 =", pow(2, p - 2, p), " equals ext-Euclid:", pow(2, p - 2, p) == mod_inverse(2, p))
    for bad in [(2, -1, 5), (2, 3, 0)]:
        try:
            mod_pow(*bad)
        except ValueError as e:
            print(f"mod_pow{bad} -> ValueError: {e}")


if __name__ == "__main__":
    main()
