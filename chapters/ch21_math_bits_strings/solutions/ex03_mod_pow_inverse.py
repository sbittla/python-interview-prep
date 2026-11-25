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

Approach ladder
---------------
1. Brute force — multiply b times, reducing mod m each step. O(b) multiplications.
   (``a ** b % m`` is worse still: a**b has about b*log2|a| bits before the reduction.)
2. Recursive  — a**b = (a**(b//2))**2 * a**(b%2). O(log b) multiplications, O(log b) stack.
3. Optimal    — iterative square-and-multiply over the bits of b. O(log b) multiplications,
   O(1) extra space. Why move up: b = 10**18 needs ~60 squarings instead of 10**18 steps.
   Production: built-in ``pow(a, b, m)``.
Inverse: extended Euclid, O(log m), works for any m with gcd(a, m) == 1. For p prime and
p not dividing a, Fermat gives pow(a, p - 2, p) (it silently returns 0 when a ≡ 0 mod p).
Python 3.8+: ``pow(a, -1, m)``.

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
    _check(b, m)
    result = 1 % m
    for _ in range(b):
        result = result * a % m
    return result


def mod_pow_recursive(a: int, b: int, m: int) -> int:
    _check(b, m)
    if b == 0:
        return 1 % m
    half = mod_pow_recursive(a, b // 2, m)
    result = half * half % m
    return result * a % m if b & 1 else result


def mod_pow(a: int, b: int, m: int) -> int:
    _check(b, m)
    result, a = 1 % m, a % m           # a % m is in [0, m) even for negative a
    while b:
        if b & 1:                      # this bit of b is set: multiply it in
            result = result * a % m
        a = a * a % m                  # a, a^2, a^4, a^8, ...
        b >>= 1
    return result


def ext_gcd(a: int, b: int) -> tuple[int, int, int]:
    old_r, r = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
        old_y, y = y, old_y - q * y
    if old_r < 0:                      # normalise so g >= 0
        old_r, old_x, old_y = -old_r, -old_x, -old_y
    return old_r, old_x, old_y


def mod_inverse(a: int, m: int) -> int:
    if m < 1:
        raise ValueError("modulus must be >= 1")
    g, x, _ = ext_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse mod {m}")
    return x % m


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
