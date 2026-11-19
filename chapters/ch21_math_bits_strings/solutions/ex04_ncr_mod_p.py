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

Approach ladder
---------------
1. Brute force — ``math.comb(n, k) % p``: exact big integer of about n bits. Fine for a few
   queries; per query O(k) big-number multiplications that grow with n.
2. Pascal table — C(i, j) = C(i-1, j-1) + C(i-1, j) mod m. O(n^2) time and space; works for
   any modulus, including non-prime.
3. Optimal    — precompute fact[i] and inv_fact[i] = (i!)^-1 mod p (one Fermat inverse, then
   inv_fact[i-1] = inv_fact[i] * i). O(n + log p) preprocessing, O(1) per query.
   Why move up: 10**5 queries with n = 10**6 are impossible with a table, trivial with this.
4. Lucas ◆   — for n >= p write n, k in base p and multiply digit-wise C(n_i, k_i).
   O(p + log_p n) with small-p factorial tables.

Follow-ups
----------
- ``math.perm(n, k)`` = n! / (n - k)!; ``math.comb(n, k)`` returns 0 when k > n.
- Next Pascal entry from the previous one: C(n, k+1) = C(n, k) * (n - k) // (k + 1) — divide
  *after* multiplying, or the integer division truncates.
"""
from __future__ import annotations

import math


def pascal_row(n: int) -> list[int]:
    if n < 0:
        raise ValueError("n must be >= 0")
    row = [1]
    for k in range(n):
        row.append(row[-1] * (n - k) // (k + 1))   # exact: the product is divisible
    return row


def ncr_table(n: int, m: int) -> list[list[int]]:
    if n < 0 or m < 1:
        raise ValueError("need n >= 0 and m >= 1")
    table = [[1 % m]]
    for i in range(1, n + 1):
        prev = table[-1]
        row = [1 % m] + [(prev[j - 1] + prev[j]) % m for j in range(1, i)] + [1 % m]
        table.append(row)
    return table


class Binomial:
    def __init__(self, n_max: int, p: int) -> None:
        if not 0 <= n_max < p:
            raise ValueError("need 0 <= n_max < p (p prime)")
        self.p = p
        fact = [1] * (n_max + 1)
        for i in range(1, n_max + 1):
            fact[i] = fact[i - 1] * i % p
        inv = [1] * (n_max + 1)
        inv[n_max] = pow(fact[n_max], p - 2, p)       # Fermat: one modular inverse
        for i in range(n_max, 0, -1):
            inv[i - 1] = inv[i] * i % p
        self.fact, self.inv_fact = fact, inv

    def comb(self, n: int, k: int) -> int:
        if k < 0 or k > n:
            return 0
        if n >= len(self.fact):
            raise ValueError("n exceeds n_max")
        return self.fact[n] * self.inv_fact[k] % self.p * self.inv_fact[n - k] % self.p


def lucas(n: int, k: int, p: int) -> int:
    if k < 0 or k > n:
        return 0
    small = Binomial(p - 1, p)
    result = 1
    while n or k:
        result = result * small.comb(n % p, k % p) % p    # a digit k_i > n_i gives 0
        n, k = n // p, k // p
    return result


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
