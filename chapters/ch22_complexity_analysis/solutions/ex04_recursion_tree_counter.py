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

Approach ladder
---------------
1. "Two recursive calls, so 2^n" — right for subsets, wrong for fib (φ^n,
   φ ≈ 1.618) and permutations (branching shrinks: n, n-1, ...).
2. Count nodes per level: level k of the permutation tree has n!/(n-k)!
   nodes; summing gives about e * n! nodes, so O(n!) nodes, not O(n^n).
3. Time = nodes x work per node + leaves x leaf work. Copying each answer
   costs n, so subsets are Θ(n * 2^n) and permutations Θ(n * n!).
   Space = recursion depth (n) + current path: O(n) beyond the output.

Follow-ups
----------
- Pruning (§18.8) cuts whole subtrees; count nodes before and after to show it.
- Why is memoised fib O(n) time but still O(n) stack depth?
"""
from __future__ import annotations

import math


def subset_tree(n: int) -> tuple[int, int, int]:
    calls = leaves = copied = 0
    path: list[int] = []

    def go(i: int) -> None:
        nonlocal calls, leaves, copied
        calls += 1
        if i == n:
            leaves += 1
            copied += len(path[:])
            return
        go(i + 1)                       # exclude item i
        path.append(i)
        go(i + 1)                       # include item i
        path.pop()

    go(0)
    return calls, leaves, copied


def perm_tree(n: int) -> tuple[int, int, int]:
    calls = leaves = copied = 0
    path: list[int] = []
    used = [False] * n

    def go() -> None:
        nonlocal calls, leaves, copied
        calls += 1
        if len(path) == n:
            leaves += 1
            copied += len(path[:])
            return
        for j in range(n):
            if not used[j]:
                used[j] = True
                path.append(j)
                go()
                path.pop()
                used[j] = False

    go()
    return calls, leaves, copied


def fib_calls(n: int) -> int:
    calls = 0

    def fib(k: int) -> int:
        nonlocal calls
        calls += 1
        return k if k < 2 else fib(k - 1) + fib(k - 2)

    fib(n)
    return calls


def memo_fib_calls(n: int) -> int:
    calls, memo = 0, {}

    def fib(k: int) -> int:
        nonlocal calls
        calls += 1
        if k in memo:
            return memo[k]
        memo[k] = k if k < 2 else fib(k - 1) + fib(k - 2)
        return memo[k]

    fib(n)
    return calls


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
