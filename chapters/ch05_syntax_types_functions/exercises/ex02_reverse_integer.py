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

Hints
-----
1. ``brute_force``: the string route is fine in Python. Handle the sign separately.
2. ``solve``: peel off the last digit repeatedly and push it onto the result. Which built-in
   returns quotient and remainder together?
3. Try ``-123 % 10`` in the REPL before deciding what number you peel digits from.
4. Python ints never overflow, so where exactly must the 32-bit check go?

Follow-ups
----------
- In a language with fixed-width ints you must check overflow *before* multiplying by 10.
- Reverse the bits instead of the digits (see Chapter 21).
"""
from __future__ import annotations

INT_MIN, INT_MAX = -(2**31), 2**31 - 1


def brute_force(x: int) -> int:
    raise NotImplementedError("TODO")


def solve(x: int) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    for x in [123, -120, 0, 1534236469, -2147483412, 10**20]:
        print(f"{x:>22} -> {solve(x):>11}   (brute agrees: {brute_force(x) == solve(x)})")
    print("floor-mod gotcha: -123 % 10 =", -123 % 10, "; -123 // 10 =", -123 // 10)


if __name__ == "__main__":
    main()
