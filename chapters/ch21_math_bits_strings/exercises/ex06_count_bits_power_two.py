"""
Exercise 06 — Counting Bits 0..n, Popcount, Power of Two       [Tier: ★ Core]
Chapter 21 · Pattern: bit tricks + DP over smaller numbers · Target time: 15 min

Problem
-------
1. ``popcount(x)`` for x >= 0 (``ValueError`` for negative x in every rung — a negative
   Python int has infinitely many 1 bits in two's complement).
2. ``count_bits(n)``: list ``[popcount(0), ..., popcount(n)]`` (n >= 0).
3. ``is_power_of_two(x)``: True for 1, 2, 4, ...; False for 0 and negatives.

Examples
--------
>>> count_bits(5)
[0, 1, 1, 2, 1, 2]
>>> [is_power_of_two(x) for x in (0, 1, 6, 8, -8)]
[False, True, False, True, False]

Constraints
-----------
- 0 <= n <= 10**6.

Hints
-----
- ``x & (x - 1)`` clears the lowest set bit.
- i and i >> 1 differ only by the last bit, which is ``i & 1``.
- A power of two has exactly one set bit.

Wrong-but-tempting
------------------
- ``x & (x - 1) == 0`` without ``x > 0``: 0 passes the test.
- Shift-and-test on a negative int: ``x >>= 1`` never reaches 0, so the loop never ends.
- ``bin(x).count("1")`` on a negative number counts the bits of |x|.

Follow-ups
----------
- Lowest set bit: ``x & -x``; index of highest set bit: ``x.bit_length() - 1``.
- Power of four: power of two and ``(x.bit_length() - 1) % 2 == 0``.
"""
from __future__ import annotations


def _nonneg(x: int) -> None:
    if x < 0:
        raise ValueError("popcount of a negative int is undefined (infinite 1 bits)")


def popcount_shift(x: int) -> int:
    raise NotImplementedError("TODO")


def popcount_kernighan(x: int) -> int:
    raise NotImplementedError("TODO")


def popcount(x: int) -> int:
    raise NotImplementedError("TODO")


def count_bits_naive(n: int) -> list[int]:
    raise NotImplementedError("TODO")


def count_bits(n: int) -> list[int]:
    raise NotImplementedError("TODO")


def is_power_of_two_loop(x: int) -> bool:
    raise NotImplementedError("TODO")


def is_power_of_two(x: int) -> bool:
    raise NotImplementedError("TODO")


def main() -> None:
    print("count_bits(16) =", count_bits(16))
    print("naive agrees   :", count_bits(1000) == count_bits_naive(1000))
    for x in [0, 1, 11, 255, 2**64 + 1]:
        print(f"popcount({x}) shift={popcount_shift(x)} kernighan={popcount_kernighan(x)} "
              f"bin={popcount(x)} bit_count={x.bit_count()}")
    for label, x in [("0", 0), ("1", 1), ("6", 6), ("64", 64), ("-8", -8),
                     ("2**100", 2**100), ("2**100 + 2", 2**100 + 2)]:
        print(f"is_power_of_two({label}) = {is_power_of_two(x)}")
    print("loop agrees  :", all(is_power_of_two(x) == is_power_of_two_loop(x) for x in range(-50, 5000)))
    x = 0b101100
    print(f"x={x:#b} lowest set bit x & -x = {x & -x:#b}  bit_length={x.bit_length()}")
    try:
        popcount(-1)
    except ValueError as e:
        print("popcount(-1) -> ValueError:", e)


if __name__ == "__main__":
    main()
