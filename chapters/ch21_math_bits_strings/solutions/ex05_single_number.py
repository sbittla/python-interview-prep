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

Approach ladder
---------------
I.  1. Counter / dict of counts. O(n) time, O(n) space.
    2. Optimal — XOR everything: x ^ x == 0 and x ^ 0 == x, XOR is commutative, so pairs
       cancel. O(n) time, O(1) space. Works for negative Python ints unchanged.
II. 1. Counter. O(n) time, O(n) space.
    2. Per-bit counting — for each of 32 bits, count how many numbers have it set; counts
       that are not multiples of 3 belong to the answer. O(32 n) time, O(1) space. Python
       ints are unbounded, so bit 31 set means *negative*: subtract 2**32 to convert.
    3. Optimal — two masks ``ones``/``twos`` hold each bit's count mod 3 (a 2-bit counter
       per bit position). O(n) time, O(1) space, and it needs no sign fix: Python's bitwise
       operators act on negative ints as if they had infinitely many leading 1 bits.
    Why move up: O(n) -> O(1) space; then 32 passes -> 1 pass.

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
    _nonempty(nums)
    return next(x for x, c in Counter(nums).items() if c == 1)


def single_one(nums: list[int]) -> int:
    _nonempty(nums)
    return reduce(xor, nums)


def to_int32(u: int) -> int:
    """Interpret the low 32 bits of u as a signed two's-complement integer."""
    u &= 0xFFFFFFFF
    return u - (1 << 32) if u >= 1 << 31 else u


def single_three_bitcount(nums: list[int], fix_sign: bool = True) -> int:
    _nonempty(nums)
    result = 0
    for bit in range(32):
        count = sum((x >> bit) & 1 for x in nums)   # >> on a negative int keeps the sign
        if count % 3:
            result |= 1 << bit
    return to_int32(result) if fix_sign else result


def single_three(nums: list[int]) -> int:
    _nonempty(nums)
    ones = twos = 0
    for x in nums:
        ones = (ones ^ x) & ~twos       # bit seen 1 time (mod 3)
        twos = (twos ^ x) & ~ones       # bit seen 2 times (mod 3)
    return ones


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
