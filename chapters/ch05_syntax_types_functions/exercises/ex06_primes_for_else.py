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

Hints
-----
1. ``brute_force_is_prime``: try every possible divisor. Why is that hopeless near 10**12?
2. If n = a * b with a <= b, how large can a be? Stop the search there, using an exact
   integer function rather than a float square root.
3. ``solve``: a loop's ``else`` block runs only when the loop was not left by ``break``.
4. Edge cases: negatives, 0, 1, 2, perfect squares, an empty or one-shot iterator.

Follow-ups
----------
- Many queries up to N? Which precomputation would you use, and at what cost?
- Rewrite ``solve`` as a one-liner without ``for … else``.
"""
from __future__ import annotations

from collections.abc import Iterable


def brute_force_is_prime(n: int) -> bool:
    raise NotImplementedError("TODO")


def is_prime(n: int) -> bool:
    raise NotImplementedError("TODO")


def solve(nums: Iterable[int]) -> int | None:
    raise NotImplementedError("TODO")


def main() -> None:
    print("primes < 30 :", [n for n in range(30) if is_prime(n)])
    print("agree <2000 :", all(is_prime(n) == brute_force_is_prime(n) for n in range(-5, 2000)))
    print("first prime :", solve([4, 6, 9, 11, 13]))
    print("none        :", solve([0, 1, -7, 8]))
    print("big prime   :", is_prime(1_000_000_007), "| Mersenne 2**31-1:", is_prime(2**31 - 1))


if __name__ == "__main__":
    main()
