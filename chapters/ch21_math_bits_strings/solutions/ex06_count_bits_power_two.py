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

Approach ladder
---------------
popcount:
1. Shift-and-test every bit. O(bit length) per number.
2. Kernighan — ``x &= x - 1`` clears the lowest set bit. O(number of set bits).
3. Built-ins — ``bin(x).count("1")`` (any version), ``x.bit_count()`` (3.10+).
count_bits(n):
1. popcount each i. O(n log n) total.
2. Optimal DP — bits[i] = bits[i >> 1] + (i & 1): i is i>>1 with one bit appended.
   O(n) time, O(n) output. Why move up: one addition per entry.
is_power_of_two:
1. Divide by 2 while even. O(log x).
2. Optimal — ``x > 0 and x & (x - 1) == 0``: a power of two has exactly one set bit. O(1)
   word operations for machine-sized values (Python ints: O(size of x)).

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
    _nonneg(x)
    count = 0
    while x:
        count += x & 1
        x >>= 1
    return count


def popcount_kernighan(x: int) -> int:
    _nonneg(x)
    count = 0
    while x:
        x &= x - 1                     # drop the lowest set bit
        count += 1
    return count


def popcount(x: int) -> int:
    _nonneg(x)
    return bin(x).count("1")           # x.bit_count() on 3.10+


def count_bits_naive(n: int) -> list[int]:
    _nonneg(n)
    return [popcount_kernighan(i) for i in range(n + 1)]


def count_bits(n: int) -> list[int]:
    _nonneg(n)
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        bits[i] = bits[i >> 1] + (i & 1)
    return bits


def is_power_of_two_loop(x: int) -> bool:
    if x <= 0:
        return False
    while x % 2 == 0:
        x //= 2
    return x == 1


def is_power_of_two(x: int) -> bool:
    return x > 0 and x & (x - 1) == 0


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
