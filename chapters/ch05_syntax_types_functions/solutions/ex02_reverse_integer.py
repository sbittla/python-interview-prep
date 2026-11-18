"""
Exercise 02 — Reverse a Signed Integer With 32-bit Clamp     [Tier: ★ Core]
Chapter 05 · Pattern: integer arithmetic · Target time: 10 min

Problem
-------
Given a signed integer x, return x with its decimal digits reversed, keeping the sign. If the
reversed value falls outside the signed 32-bit range [-2**31, 2**31 - 1], return 0. Python ints
never overflow, so the range check must be written explicitly.

Examples
--------
>>> solve(123)
321
>>> solve(-120)
-21
>>> solve(1534236469)
0

Constraints
-----------
- x is any Python int (the 32-bit rule applies to the result only)

Approach ladder
---------------
1. Brute force — convert abs(x) to str, reverse with [::-1], convert back, reapply the sign.
   O(d) time and O(d) space for d digits. Perfectly acceptable in Python interviews.
2. Optimal    — peel digits with divmod(n, 10) on the absolute value and build the result
   arithmetically. O(d) time, O(1) extra space. Interviewers who come from C/Java often want
   this version because it shows you understand digit arithmetic. Work on abs(x): Python's //
   and % floor towards negative infinity, so -123 % 10 == 7, not -3.

Follow-ups
----------
- In a language with fixed-width ints you must check overflow *before* multiplying by 10.
- Reverse the bits instead of the digits (see Chapter 21).
"""
from __future__ import annotations

INT_MIN, INT_MAX = -(2**31), 2**31 - 1


def brute_force(x: int) -> int:
    sign = -1 if x < 0 else 1
    result = sign * int(str(abs(x))[::-1])
    return result if INT_MIN <= result <= INT_MAX else 0


def solve(x: int) -> int:
    sign = -1 if x < 0 else 1
    n, result = abs(x), 0
    while n:
        n, digit = divmod(n, 10)
        result = result * 10 + digit
    result *= sign
    return result if INT_MIN <= result <= INT_MAX else 0


def main() -> None:
    for x in [123, -120, 0, 1534236469, -2147483412, 10**20]:
        print(f"{x:>22} -> {solve(x):>11}   (brute agrees: {brute_force(x) == solve(x)})")
    print("floor-mod gotcha: -123 % 10 =", -123 % 10, "; -123 // 10 =", -123 // 10)


if __name__ == "__main__":
    main()
