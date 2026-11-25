"""
Exercise 04 — Recursion-Tree Node Counter                 [Tier: ★ Core]
Chapter 22 · Pattern: count calls x work per call · Target time: 20 min

Problem
-------
Instrument three classic recursions and count, by actually running them:

- ``subset_tree(n)``  — include/exclude backtracking over n items. Return
  ``(calls, leaves, copied)`` where ``copied`` is the total number of elements
  copied when each leaf saves ``path[:]``.
- ``perm_tree(n)``    — permutations with a ``used`` array (choose any unused
  item at each level). Same triple.
- ``fib_calls(n)``    — calls made by naive ``fib(n) = fib(n-1) + fib(n-2)``,
  fib(0) = 0, fib(1) = 1; and ``memo_fib_calls(n)``, calls when every call
  first checks a memo dict (a cache hit still counts as a call).

Then check each count against its closed form:

    subsets:      calls = 2^(n+1) - 1, leaves = 2^n, copied = n * 2^(n-1)
    permutations: calls = sum_{k=0..n} n!/(n-k)!  ( = floor(e * n!) for n >= 1 ),
                  leaves = n!, copied = n * n!
    naive fib:    calls = 2 * F(n+1) - 1  (F = Fibonacci numbers) = Θ(φ^n)
    memo fib:     calls = 2n - 1 for n >= 1

Examples
--------
>>> subset_tree(3)
(15, 8, 12)
>>> perm_tree(3)
(16, 6, 18)
>>> fib_calls(5)
15

Constraints
-----------
- 0 <= n <= 20 for subsets and fib, n <= 9 for permutations.

Hints
-----
- Increment a nonlocal counter at the top of every call (including leaves).
- At a leaf, add len(path) to ``copied`` (that is what path[:] costs).
- Permutations: loop over all j, skip used ones; mark, recurse, unmark.
- Memoised fib: count the call before checking the memo.

Follow-ups
----------
- Pruning (§18.8) cuts whole subtrees; count nodes before and after to show it.
- Why is memoised fib O(n) time but still O(n) stack depth?
"""
from __future__ import annotations

import math


def subset_tree(n: int) -> tuple[int, int, int]:
    raise NotImplementedError("TODO")


def perm_tree(n: int) -> tuple[int, int, int]:
    raise NotImplementedError("TODO")


def fib_calls(n: int) -> int:
    raise NotImplementedError("TODO")


def memo_fib_calls(n: int) -> int:
    raise NotImplementedError("TODO")


def fibonacci(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def perm_nodes_formula(n: int) -> int:
    return sum(math.factorial(n) // math.factorial(n - k) for k in range(n + 1))


def main() -> None:
    print(" n  subset calls/leaves/copied   perm calls/leaves/copied   e*n!")
    for n in range(1, 8):
        s, p = subset_tree(n), perm_tree(n)
        print(f"{n:>2}  {s[0]:>6} {s[1]:>5} {s[2]:>6}           "
              f"{p[0]:>6} {p[1]:>5} {p[2]:>6}      {math.e * math.factorial(n):9.1f}")
    ok_sub = all(subset_tree(n) == (2 ** (n + 1) - 1, 2 ** n, n * 2 ** (n - 1) if n else 0)
                 for n in range(0, 15))
    ok_perm = all(perm_tree(n) == (perm_nodes_formula(n), math.factorial(n), n * math.factorial(n))
                  for n in range(0, 8))
    ok_e = all(perm_nodes_formula(n) == math.floor(math.e * math.factorial(n)) for n in range(1, 15))
    print(f"subset closed forms hold n=0..14: {ok_sub}")
    print(f"perm closed forms hold n=0..7: {ok_perm}; floor(e*n!) matches n=1..14: {ok_e}")
    print(f"{'n':>3} {'naive fib calls':>16} {'2F(n+1)-1':>10} {'memo calls':>11}")
    for n in (5, 10, 20):
        print(f"{n:>3} {fib_calls(n):>16} {2 * fibonacci(n + 1) - 1:>10} {memo_fib_calls(n):>11}")
    print(f"naive fib calls ratio n=20/n=19: {fib_calls(20) / fib_calls(19):.3f} (phi = 1.618)")


if __name__ == "__main__":
    main()
