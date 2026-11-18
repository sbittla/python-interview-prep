"""
Exercise 03 — Infinite Generators: Fibonacci and Primes      [Tier: ★ Core]
Chapter 23 · Pattern: generators + islice · Target time: 15 min

Problem
-------
1. ``fibonacci()`` yields 0, 1, 1, 2, 3, 5, ... forever.
2. ``primes()`` yields 2, 3, 5, 7, 11, ... forever.
3. ``take(n, iterable)`` returns the first n items as a list (works on infinite iterators).

Examples
--------
>>> take(7, fibonacci())
[0, 1, 1, 2, 3, 5, 8]
>>> take(5, primes())
[2, 3, 5, 7, 11]

Constraints
-----------
- Generators must be lazy: producing k items costs only the work for k items.
- ``take`` with n <= 0 returns ``[]``.

Hints
-----
- ``itertools.islice(it, n)`` stops after n items; never call ``list()`` on an infinite generator.
- For primes, keep the primes found so far and test candidates only against primes p with p*p <= n.

Approach ladder
---------------
1. Return a list of the first N values — caller must know N up front.
2. Generator with trial division by all smaller numbers — lazy, O(n) per candidate.
3. Trial division only by known primes up to sqrt(candidate) — O(sqrt(n)/log n) per candidate.
   (An incremental sieve with a dict of composites is the next rung; see follow-ups.)

Follow-ups
----------
- Write the incremental Sieve of Eratosthenes as a generator (``dict`` of next composites).
- How would you get the 1000th Fibonacci number without storing the first 999?
"""
from __future__ import annotations

from itertools import count, islice


def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def primes():
    found: list[int] = []
    for n in count(2):
        if all(n % p for p in found if p * p <= n):
            found.append(n)
            yield n


def primes_sieve():
    """Incremental sieve: maps each upcoming composite to the primes that produce it."""
    composites: dict[int, list[int]] = {}
    for n in count(2):
        if n not in composites:
            yield n
            composites[n * n] = [n]
        else:
            for p in composites.pop(n):
                composites.setdefault(n + p, []).append(p)


def take(n: int, iterable) -> list:
    return list(islice(iterable, max(n, 0)))


def nth(iterable, n: int, default=None):
    """Return the n-th item (0-based) or default."""
    return next(islice(iterable, n, None), default)


def main() -> None:
    print("fibonacci:", take(12, fibonacci()))
    print("primes   :", take(12, primes()))
    print("sieve    :", take(12, primes_sieve()))
    print("agree on first 500:", take(500, primes()) == take(500, primes_sieve()))
    print("take(0)  :", take(0, fibonacci()))
    print("100th fibonacci (0-based):", nth(fibonacci(), 100))
    print("nth past end of finite iterable:", nth(iter([1, 2]), 5, "missing"))
    gen = fibonacci()
    print("same generator continues:", take(3, gen), take(3, gen))


if __name__ == "__main__":
    main()
