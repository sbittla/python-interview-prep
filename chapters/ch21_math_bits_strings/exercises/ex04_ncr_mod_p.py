"""
Exercise 04 — nCr mod p and Pascal's Triangle                 [Tier: ★ Core]
Chapter 21 · Pattern: combinatorics, factorial tables · Target time: 20 min

Problem
-------
1. ``pascal_row(n)``: row n of Pascal's triangle, exact ([1] for n = 0).
2. ``ncr_table(n, m)``: table C[i][j] mod m for 0 <= j <= i <= n (any modulus m >= 1).
3. ``Binomial(n_max, p)``: answer many queries C(n, k) mod p in O(1) each for n <= n_max < p,
   p prime. C(n, k) = 0 when k < 0 or k > n.
4. ◆ ``lucas(n, k, p)``: C(n, k) mod p for huge n with a small prime p.

Examples
--------
>>> pascal_row(5)
[1, 5, 10, 10, 5, 1]
>>> Binomial(10, 10**9 + 7).comb(10, 3)
120
>>> lucas(10**18, 10**9, 13) == 0      # matches math.comb(...) % 13 by Lucas' theorem
True

Constraints
-----------
- ``Binomial`` needs p prime and n_max < p (else n! ≡ 0 and has no inverse).

Hints
-----
- Pascal row from the previous entry: multiply by (n - k), *then* divide by (k + 1).
- Pascal table works for any modulus because it only adds.
- Factorials mod p plus one Fermat inverse of n_max!; walk the inverse factorials downwards
  with ``inv_fact[i - 1] = inv_fact[i] * i``.
- Lucas: multiply C(n_i, k_i) over the base-p digits of n and k.

Wrong-but-tempting
------------------
- ``row[-1] * ((n - k) // (k + 1))``: dividing first truncates.
- Using the factorial formula with a non-prime modulus, or with n >= p (n! ≡ 0 mod p).
- Forgetting C(n, k) = 0 for k < 0 or k > n (index -1 wraps around in Python).

Follow-ups
----------
- ``math.perm(n, k)`` = n! / (n - k)!; ``math.comb(n, k)`` returns 0 when k > n.
- Next Pascal entry from the previous one: C(n, k+1) = C(n, k) * (n - k) // (k + 1) — divide
  *after* multiplying, or the integer division truncates.
"""
from __future__ import annotations

import math


def pascal_row(n: int) -> list[int]:
    raise NotImplementedError("TODO")


def ncr_table(n: int, m: int) -> list[list[int]]:
    raise NotImplementedError("TODO")


class Binomial:
    def __init__(self, n_max: int, p: int) -> None:
        raise NotImplementedError("TODO")

    def comb(self, n: int, k: int) -> int:
        raise NotImplementedError("TODO")


def lucas(n: int, k: int, p: int) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    for n in range(6):
        print(f"row {n}: {pascal_row(n)}")
    print("pascal_row(20) == [comb(20,k)]:", pascal_row(20) == [math.comb(20, k) for k in range(21)])
    print("ncr_table(6, 4)[6] =", ncr_table(6, 4)[6], " (non-prime modulus)")
    p = 10**9 + 7
    b = Binomial(10**5, p)
    for n, k in [(10, 3), (100000, 50000), (5, 7), (5, -1), (0, 0)]:
        print(f"C({n}, {k}) mod p = {b.comb(n, k)}  math.comb % p = {math.comb(n, k) % p if k >= 0 else 0}")
    for n, k, q in [(10, 3, 7), (1000, 300, 13), (10**18, 10**9, 13)]:
        check = math.comb(n, k) % q if n < 10**4 else "too big to check"
        print(f"lucas({n}, {k}, {q}) = {lucas(n, k, q)}  check={check}")
    print("math.perm(5, 2) =", math.perm(5, 2), " math.comb(5, 7) =", math.comb(5, 7))


if __name__ == "__main__":
    main()
