"""
Exercise 06 — Primality and First Prime With `for … else`     [Tier: ★ Core]
Chapter 05 · Pattern: loops with early exit · Target time: 10 min

Problem
-------
Write ``is_prime(n)`` and ``solve(nums)``. ``solve`` returns the first prime in the iterable
``nums`` or ``None`` when there is none. Use ``for … else`` at least once: the ``else`` block of
a loop runs only when the loop finished without ``break``.

Examples
--------
>>> [n for n in range(20) if is_prime(n)]
[2, 3, 5, 7, 11, 13, 17, 19]
>>> solve([4, 6, 9, 11, 13])
11
>>> solve([1, 4, 6]) is None
True

Constraints
-----------
- integers may be negative or zero (neither is prime); n <= 10**12 for is_prime

Approach ladder
---------------
1. Brute force — test every divisor 2..n-1. O(n) per number: far too slow for n ~ 10**12.
2. Optimal    — handle 2 and evens, then test odd divisors up to isqrt(n): a composite n has a
   factor <= sqrt(n). O(sqrt n) per number. Use ``math.isqrt`` (exact integer square root),
   not ``int(n ** 0.5)``, which can be off by one for big n because of float rounding.

Follow-ups
----------
- Many queries up to N? Precompute a Sieve of Eratosthenes, O(N log log N) (Chapter 21).
- Rewrite ``solve`` with ``next((x for x in nums if is_prime(x)), None)``.
"""
from __future__ import annotations

from collections.abc import Iterable
from math import isqrt


def brute_force_is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, n):
        if n % d == 0:
            return False
    return True


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for d in range(3, isqrt(n) + 1, 2):
        if n % d == 0:
            break               # found a factor: skip the else block
    else:
        return True             # loop ran to completion: no factor found
    return False


def solve(nums: Iterable[int]) -> int | None:
    for x in nums:
        if is_prime(x):
            found = x
            break
    else:
        found = None            # no break happened
    return found


def main() -> None:
    print("primes < 30 :", [n for n in range(30) if is_prime(n)])
    print("agree <2000 :", all(is_prime(n) == brute_force_is_prime(n) for n in range(-5, 2000)))
    print("first prime :", solve([4, 6, 9, 11, 13]))
    print("none        :", solve([0, 1, -7, 8]))
    print("big prime   :", is_prime(1_000_000_007), "| Mersenne 2**31-1:", is_prime(2**31 - 1))


if __name__ == "__main__":
    main()
