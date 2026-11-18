"""
Exercise 11 — A Primality Test That Gives Up Too Early  [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (control flow) · Target time: 5 min

Problem
-------
`is_prime(n)` must return True exactly when n is prime. The buggy version puts
`else: return True` on the `if` INSIDE the loop, so it decides after testing a
single divisor: 9 is reported prime because 9 % 2 != 0.
`first_divisor(n)` returns the smallest divisor d with 2 <= d <= sqrt(n), or None.

Examples
--------
>>> [n for n in range(20) if is_prime(n)]
[2, 3, 5, 7, 11, 13, 17, 19]
>>> first_divisor(91), first_divisor(97)
(7, None)

Constraints
-----------
- 0 <= n <= 10**9 (trial division up to sqrt(n) is fast enough for one query).

Approach ladder
---------------
1. Buggy  — `else` bound to the `if`, returning on the first iteration.
2. Fixed  — `for ... else`: the loop's `else` runs only if the loop finished
   WITHOUT `break`. Or simply `return True` after the loop. O(sqrt n) time.

Follow-ups
----------
- Does `while ... else` exist? (Yes, same rule: runs if no `break`.)
- What does `for ... else` do on an EMPTY iterable? (Runs the else block.)
- Many primes up to N? → Sieve of Eratosthenes, O(N log log N).
"""
from __future__ import annotations

import math


def buggy_is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, math.isqrt(n) + 1):
        if n % d == 0:
            return False
        else:
            return True
    return True


def first_divisor(n: int) -> int | None:
    """Smallest d in [2, isqrt(n)] dividing n, else None (for ... else demo)."""
    for d in range(2, math.isqrt(n) + 1):
        if n % d == 0:
            found = d
            break
    else:                      # no break: the loop ran to completion
        found = None
    return found


def is_prime(n: int) -> bool:
    """Trial division up to isqrt(n): O(sqrt n)."""
    return n >= 2 and first_divisor(n) is None


def main() -> None:
    print("buggy primes < 30:", [n for n in range(30) if buggy_is_prime(n)])
    print("fixed primes < 30:", [n for n in range(30) if is_prime(n)])
    print("first_divisor(91):", first_divisor(91))
    print("first_divisor(97):", first_divisor(97))
    print("first_divisor(3) (empty loop -> else):", first_divisor(3))


if __name__ == "__main__":
    main()
