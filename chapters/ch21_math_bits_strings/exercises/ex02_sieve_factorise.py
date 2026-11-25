"""
Exercise 02 — Sieve, Smallest-Prime-Factor Table, Segmented Sieve   [Tier: ★ Core]
Chapter 21 · Pattern: sieve of Eratosthenes · Target time: 20 min

Problem
-------
1. ``sieve(n)``: all primes <= n, ascending ([] when n < 2).
2. ``spf_table(n)`` and ``factorise(x, spf)``: smallest-prime-factor table for 0..n, then the
   prime factorisation of any 2 <= x <= n as a sorted list with repeats
   (``factorise(1, spf) == []``).
3. ◆ ``segmented_sieve(lo, hi)``: primes in [lo, hi] when hi is too large to sieve from 0
   but hi - lo is small.

Examples
--------
>>> sieve(30)
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
>>> factorise(360, spf_table(400))
[2, 2, 2, 3, 3, 5]
>>> segmented_sieve(100, 130)
[101, 103, 107, 109, 113, 127]

Constraints
-----------
- n <= 10**7 for ``sieve``; for ``segmented_sieve`` hi <= 10**12 and hi - lo <= 10**6.

Hints
-----
- ``bytearray`` of flags; for each p up to ``isqrt(n)`` that is still marked, clear
  p*p, p*p+p, ... with one slice assignment.
- SPF table: the first prime to reach k is its smallest prime factor; only write unset slots.
- Segmented: sieve the base primes up to isqrt(hi), then find the first multiple of each p
  inside [lo, hi] with ceiling division.

Wrong-but-tempting
------------------
- ``int(n ** 0.5)``: float rounding is wrong for large n; use ``math.isqrt``.
- Starting the crossing-off at 2*p (correct but slower) or at p (crosses off p itself).
- In the segmented sieve, forgetting ``max(p * p, ...)``: a base prime inside [lo, hi] is
  crossed off as its own multiple. Also forgetting that 0 and 1 are not prime.

Follow-ups
----------
- Count primes below n: ``sum(is_prime_flags)``.
- Why start at p*p? Every smaller multiple k*p has k < p, so a smaller prime factor removed it.
- Use ``math.isqrt``, never ``int(n ** 0.5)`` (float rounding for large n).
"""
from __future__ import annotations

from math import isqrt


def primes_trial(n: int) -> list[int]:
    """Rung 1 (the per-number test lives in Chapter 5, ex06)."""
    raise NotImplementedError("TODO")


def sieve(n: int) -> list[int]:
    raise NotImplementedError("TODO")


def spf_table(n: int) -> list[int]:
    raise NotImplementedError("TODO")


def factorise(x: int, spf: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def segmented_sieve(lo: int, hi: int) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    print("sieve(30)      =", sieve(30))
    print("trial(30)      =", primes_trial(30))
    print("sieve(1), sieve(2) =", sieve(1), sieve(2))
    print("count <= 10**6 =", len(sieve(10**6)))
    spf = spf_table(1000)
    for x in [1, 2, 360, 997, 999, 1000]:
        print(f"factorise({x}) = {factorise(x, spf)}")
    print("segmented(100, 130)     =", segmented_sieve(100, 130))
    print("segmented(10**12, +100) =", segmented_sieve(10**12, 10**12 + 100))
    print("segmented(0, 10)        =", segmented_sieve(0, 10))


if __name__ == "__main__":
    main()
