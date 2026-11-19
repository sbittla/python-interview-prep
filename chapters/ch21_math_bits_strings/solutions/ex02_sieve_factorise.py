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

Approach ladder
---------------
1. Brute force — trial division of every k <= n (Chapter 5, ex06). O(n sqrt n) time.
2. Optimal    — sieve: for each prime p <= isqrt(n) cross off p*p, p*p+p, ... (smaller
   multiples were already crossed off by smaller primes). O(n log log n) time, O(n) space.
   Why move up: one pass serves every query up to n.
3. SPF table  — record the *smallest* prime that crosses k off; factorising x is then
   repeated division by spf[x]: O(log x) per query after O(n log log n) preprocessing.
4. Segmented ◆ — sieve base primes up to isqrt(hi), then cross off their multiples inside
   [lo, hi] only. O(sqrt(hi) log log hi + (hi - lo + 1) log log hi) time, O(sqrt(hi) + hi - lo) space.

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
    def is_prime(k: int) -> bool:
        if k < 2:
            return False
        return all(k % d for d in range(2, isqrt(k) + 1))
    return [k for k in range(n + 1) if is_prime(k)]


def sieve(n: int) -> list[int]:
    if n < 2:
        return []
    flags = bytearray([1]) * (n + 1)
    flags[0] = flags[1] = 0
    for p in range(2, isqrt(n) + 1):
        if flags[p]:
            flags[p * p::p] = bytes(len(range(p * p, n + 1, p)))   # cross off in C
    return [k for k in range(n + 1) if flags[k]]


def spf_table(n: int) -> list[int]:
    spf = list(range(n + 1))            # spf[k] == k means "no smaller factor found yet"
    for p in range(2, isqrt(n) + 1):
        if spf[p] == p:                 # p is prime
            for q in range(p * p, n + 1, p):
                if spf[q] == q:
                    spf[q] = p
    return spf


def factorise(x: int, spf: list[int]) -> list[int]:
    if not 1 <= x < len(spf):
        raise ValueError(f"x must be in 1..{len(spf) - 1}")
    out = []
    while x > 1:
        p = spf[x]
        out.append(p)
        x //= p
    return out


def segmented_sieve(lo: int, hi: int) -> list[int]:
    lo = max(lo, 2)
    if hi < lo:
        return []
    flags = bytearray([1]) * (hi - lo + 1)          # flags[i] <-> number lo + i
    for p in sieve(isqrt(hi)):
        start = max(p * p, (lo + p - 1) // p * p)   # first multiple of p in range, >= p*p
        flags[start - lo::p] = bytes(len(range(start, hi + 1, p)))
    return [lo + i for i, f in enumerate(flags) if f]


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
