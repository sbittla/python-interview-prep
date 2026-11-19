"""
Exercise 01 — Operation Counter and Growth Fitter          [Tier: ★ Core]
Chapter 08 · Pattern: count operations, fit a growth class · Target time: 20 min

Problem
-------
Timings are noisy; operation counts are not. Build two tools:

1. ``growth_ratios(points)`` — given ``{n: count}`` measured at several input
   sizes, return ``count(n_next) / count(n)`` for each consecutive pair (rounded
   to 2 decimals). When n doubles, O(n) gives ~2, O(n^2) ~4, O(n^3) ~8, O(log n)
   and O(1) ~1, O(n log n) a bit above 2.
2. ``fit_growth(points)`` — return the label from ``CLASSES`` whose shape g(n)
   best explains the counts: the class for which ``count / g(n)`` stays most
   nearly constant. Compare in log space so 2^n and n! never overflow:
   spread(g) = max(ln count − ln g(n)) − min(ln count − ln g(n)); pick the
   smallest spread; on a tie (within 1e-9) pick the slower-growing class.

Use them on instrumented algorithms (``linear_scan``, ``merge_sort_count``,
``all_pairs``, ``subsets_count``, ``permutations_count`` ...), each of which
returns the number of times its innermost step ran.

Examples
--------
>>> fit_growth({64: 64, 128: 128, 256: 256})
'O(n)'
>>> growth_ratios({64: 4096, 128: 16384, 256: 65536})
[4.0, 4.0]
>>> fit_growth({64: 6, 128: 7, 256: 8, 512: 9})
'O(log n)'

Constraints
-----------
- At least 2 points; every n >= 2 and every count >= 1 (else ValueError).
- Standard library only; results must be deterministic (no timing).

Hints
-----
- Sort the points by n; zip consecutive pairs for the ratios.
- For each class compute ln(count) - ln g(n) per point; the right class keeps
  these residuals nearly equal (smallest max - min).
- Iterate CLASSES in order and replace the best only on a strictly smaller spread.

Follow-ups
----------
- Why do lower-order terms (3n + 5) not fool the fit? Their share of the
  count shrinks as n grows; use sizes at least 8x apart.
- Fit Theta(phi^n) Fibonacci recursion: it lands near O(2^n) — a valid upper bound but
  not tight (→ §22.4).
"""
from __future__ import annotations

import math
import random

# ln g(n) for each class, ordered from slowest- to fastest-growing.
CLASSES: dict[str, object] = {
    "O(1)": lambda n: 0.0,
    "O(log n)": lambda n: math.log(math.log2(n)),
    "O(n)": lambda n: math.log(n),
    "O(n log n)": lambda n: math.log(n * math.log2(n)),
    "O(n^2)": lambda n: 2 * math.log(n),
    "O(n^3)": lambda n: 3 * math.log(n),
    "O(2^n)": lambda n: n * math.log(2),
    "O(n!)": lambda n: math.lgamma(n + 1),
}


def _validate(points: dict[int, int]) -> list[tuple[int, int]]:
    if len(points) < 2:
        raise ValueError("need at least two (n, count) points")
    items = sorted(points.items())
    if any(n < 2 or c < 1 for n, c in items):
        raise ValueError("every n must be >= 2 and every count >= 1")
    return items


def growth_ratios(points: dict[int, int]) -> list[float]:
    raise NotImplementedError("TODO")


def fit_growth(points: dict[int, int]) -> str:
    raise NotImplementedError("TODO")


# ---------- instrumented algorithms: each returns its innermost-step count ----------

def constant_work(n: int) -> int:
    return sum(1 for _ in range(10))              # ignores n


def halving(n: int) -> int:
    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps


def linear_scan(n: int) -> int:
    steps = 0
    for _ in range(n):
        steps += 1
    return 3 * steps + 5                          # constants and lower terms on purpose


def merge_sort_count(n: int) -> int:
    """Merge-sort a seeded shuffle of range(n); count element moves during merges."""
    data = list(range(n))
    random.Random(n).shuffle(data)
    moves = 0

    def sort(xs: list[int]) -> list[int]:
        nonlocal moves
        if len(xs) <= 1:
            return xs
        mid = len(xs) // 2
        left, right = sort(xs[:mid]), sort(xs[mid:])
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                out.append(left[i]); i += 1
            else:
                out.append(right[j]); j += 1
        out += left[i:] + right[j:]
        moves += len(out)
        return out

    assert sort(data) == sorted(data)
    return moves


def all_pairs(n: int) -> int:
    return sum(1 for i in range(n) for j in range(i + 1, n))


def all_triples(n: int) -> int:
    return sum(1 for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n))


def subsets_count(n: int) -> int:
    """Include/exclude recursion; count the leaves (one per subset)."""
    def go(i: int) -> int:
        return 1 if i == n else go(i + 1) + go(i + 1)
    return go(0)


def permutations_count(n: int) -> int:
    """Swap-based permutation generator; count complete permutations."""
    a = list(range(n))

    def go(k: int) -> int:
        if k == n:
            return 1
        total = 0
        for i in range(k, n):
            a[k], a[i] = a[i], a[k]
            total += go(k + 1)
            a[k], a[i] = a[i], a[k]
        return total
    return go(0)


DEMOS = [
    (constant_work, (64, 128, 256, 512, 1024)),
    (halving, (64, 128, 256, 512, 1024)),
    (linear_scan, (64, 128, 256, 512, 1024)),
    (merge_sort_count, (64, 128, 256, 512, 1024)),
    (all_pairs, (64, 128, 256, 512)),
    (all_triples, (16, 32, 64, 128)),
    (subsets_count, (8, 10, 12, 14)),
    (permutations_count, (4, 5, 6, 7)),
]


def main() -> None:
    for fn, sizes in DEMOS:
        points = {n: fn(n) for n in sizes}
        print(f"{fn.__name__:<19} counts={list(points.values())}")
        print(f"{'':<19} ratios={growth_ratios(points)} -> {fit_growth(points)}")
    for bad in ({8: 1}, {1: 5, 4: 9}):
        try:
            fit_growth(bad)
        except ValueError as exc:
            print(f"fit_growth({bad}) -> ValueError: {exc}")


if __name__ == "__main__":
    main()
