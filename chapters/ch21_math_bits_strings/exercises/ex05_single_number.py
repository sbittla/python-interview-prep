"""
Exercise 05 — Single Number I and II                          [Tier: ★ Core]
Chapter 21 · Pattern: XOR cancellation, per-bit counting · Target time: 20 min

Problem
-------
I.  Every value in ``nums`` appears exactly twice except one, which appears once. Return it.
II. Every value appears exactly three times except one, which appears once. Return it.
Values are 32-bit signed integers (-2**31 <= x < 2**31) and may be negative. Use O(1) extra
space for the optimal rung. An empty list raises ``ValueError`` in every rung.

Examples
--------
>>> single_one([4, 1, 2, 1, 2])
4
>>> single_three([2, 2, 3, 2]), single_three([-2, -2, 1, 1, -3, 1, -3, -3, -4, -2])
(3, -4)

Constraints
-----------
- 1 <= len(nums) <= 3 * 10**4; the input is promised valid (no validation beyond emptiness).

Hints
-----
- x ^ x == 0 and x ^ 0 == x; XOR is commutative and associative.
- For "three times", count each bit position modulo 3.
- Bit 31 in the per-bit count means the answer is negative: convert from 32-bit two's
  complement.
- Two masks ``ones`` and ``twos`` can hold a counter mod 3 for all 32 bits at once.

Wrong-but-tempting
------------------
- XOR for the "three times" variant: three copies XOR to x, not 0.
- Per-bit counting without the sign fix: -4 comes back as 4294967292.
- ``(3 * sum(set(nums)) - sum(nums)) // 2`` is correct but uses O(n) extra space for the set,
  so it does not meet the O(1)-space requirement.

Follow-ups
----------
- Single Number III: two singles -> XOR all, split by lowest set bit ``x & -x``.
- Missing number in 0..n: XOR indices with values.
"""
from __future__ import annotations

from collections import Counter
from functools import reduce
from operator import xor


def _nonempty(nums: list[int]) -> None:
    if not nums:
        raise ValueError("nums is empty")


def single_brute(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def single_one(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def to_int32(u: int) -> int:
    """Interpret the low 32 bits of u as a signed two's-complement integer."""
    raise NotImplementedError("TODO")


def single_three_bitcount(nums: list[int], fix_sign: bool = True) -> int:
    raise NotImplementedError("TODO")


def single_three(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    for nums in [[4, 1, 2, 1, 2], [-7, 3, 3], [0]]:
        print(f"I  {nums!s:<18} xor={single_one(nums):<4} counter={single_brute(nums)}")
    for nums in [[2, 2, 3, 2], [0, 1, 0, 1, 0, 1, 99], [-2, -2, 1, 1, -3, 1, -3, -3, -4, -2],
                 [-2**31, 5, 5, 5]]:
        print(f"II {nums}\n   fsm={single_three(nums)} bitcount={single_three_bitcount(nums)} "
              f"no-sign-fix={single_three_bitcount(nums, fix_sign=False)} counter={single_brute(nums)}")
    print("bin(-5) =", bin(-5), " -5 & 0xFFFFFFFF =", -5 & 0xFFFFFFFF,
          " to_int32 back =", to_int32(-5 & 0xFFFFFFFF), " ~5 =", ~5)
    try:
        single_three([])
    except ValueError as e:
        print("single_three([]) -> ValueError:", e)


if __name__ == "__main__":
    main()
