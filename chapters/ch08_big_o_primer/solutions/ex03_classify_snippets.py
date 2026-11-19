"""
Exercise 03 — Classify Ten Snippets, Then Prove It          [Tier: ★ Core]
Chapter 08 · Pattern: loop/recursion shape -> growth class · Target time: 15 min

Problem
-------
Each function ``s01`` ... ``s10`` below is a small snippet instrumented to
return how many times its innermost step ran for input size n. Without running
anything, fill ``ANSWERS`` with the tight Big-O time class of every snippet,
using the labels of ex01 (``"O(1)"``, ``"O(log n)"``, ``"O(n)"``,
``"O(n log n)"``, ``"O(n^2)"``, ``"O(n^3)"``, ``"O(2^n)"``, ``"O(n!)"``).
Then check yourself: ``measured(name)`` runs the snippet at several sizes and
fits the class with ``ex01_op_counter.fit_growth``.

Examples
--------
>>> measured("s01")
'O(n)'
>>> ANSWERS["s01"] == measured("s01")
True

Constraints
-----------
- Snippet s10 counts real ``__eq__`` calls made by ``x not in list`` through
  the ``Probe`` wrapper, so the hidden cost is measured, not assumed.

Hints
-----
- Sequential loops add; nested loops multiply.
- A loop variable that halves or doubles gives log n iterations.
- n + n/2 + n/4 + ... is at most 2n.
- A function that calls itself twice on n - 1 builds a tree with 2ⁿ leaves.

Follow-ups
----------
- Which snippet's *space* is not O(1)? (s09: recursion depth n; s10: the list.)
- Rewrite s10 in O(n) with a set (ex04).
"""
from __future__ import annotations

from ex01_op_counter import fit_growth


class Probe:
    """Int wrapper that counts how often == is called on it."""
    eq_calls = 0

    def __init__(self, v: int) -> None:
        self.v = v

    def __eq__(self, other: object) -> bool:
        Probe.eq_calls += 1
        return isinstance(other, Probe) and self.v == other.v

    def __hash__(self) -> int:
        return hash(self.v)


def s01(n):
    ops = 0
    for i in range(n):
        ops += 1
    return ops


def s02(n):
    ops = 0
    for i in range(n):
        ops += 1
    for j in range(n):
        ops += 1
    return ops


def s03(n):
    ops = 0
    for i in range(n):
        for j in range(n):
            ops += 1
    return ops


def s04(n):
    ops = 0
    for i in range(n):
        for j in range(i):
            ops += 1
    return ops


def s05(n):
    ops = 0
    while n > 1:
        n //= 2
        ops += 1
    return ops


def s06(n):
    ops = 0
    for i in range(n):
        j = 1
        while j < n:
            j *= 2
            ops += 1
    return ops


def s07(n):
    ops = 0
    i = n
    while i > 0:
        for j in range(i):
            ops += 1
        i //= 2
    return ops


def s08(n):
    ops = 0
    for i in range(100):
        ops += 1
    return ops


def s09(n):
    if n == 0:
        return 1
    return s09(n - 1) + s09(n - 1)


def s10(n):
    Probe.eq_calls = 0
    seen = []
    for x in [Probe(i) for i in range(n)]:
        if x not in seen:
            seen.append(x)
    return max(1, Probe.eq_calls)


SIZES = {"s09": (8, 10, 12, 14)}         # exponential: keep n small
DEFAULT_SIZES = (64, 128, 256, 512, 1024)

ANSWERS = {
    "s01": "O(n)", "s02": "O(n)", "s03": "O(n^2)", "s04": "O(n^2)", "s05": "O(log n)",
    "s06": "O(n log n)", "s07": "O(n)", "s08": "O(1)", "s09": "O(2^n)", "s10": "O(n^2)",
}


def measured(name: str) -> str:
    fn = globals()[name]
    return fit_growth({n: fn(n) for n in SIZES.get(name, DEFAULT_SIZES)})


def main() -> None:
    score = 0
    for name in sorted(ANSWERS):
        got = measured(name)
        ok = got == ANSWERS[name]
        score += ok
        print(f"{name}: answer={ANSWERS[name]:<11} measured={got:<11} match={ok}")
    print(f"score {score}/{len(ANSWERS)}")


if __name__ == "__main__":
    main()
