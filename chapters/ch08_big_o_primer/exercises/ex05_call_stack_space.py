"""
Exercise 05 — Space on the Call Stack                        [Tier: ★ Core]
Chapter 08 · Pattern: recursion depth = stack space · Target time: 15 min

Problem
-------
Three ways to sum a list ``xs`` use the same O(n) time but very different
extra space. Implement each so it also reports the deepest recursion level it
reached (count the outermost call as depth 1; a loop has depth 0):

- ``sum_linear(xs)``   — recursive: ``xs[i] + sum(i + 1)``      -> depth n + 1
- ``sum_halves(xs)``   — recursive on the two halves [lo, mid), [mid, hi)
                          -> depth about log2 n
- ``sum_loop(xs)``     — a for-loop with one accumulator         -> depth 0

Each returns ``(total, max_depth)``. Then ``hits_recursion_limit(fn, n)``
returns True when ``fn(list(range(n)))`` raises RecursionError under CPython's
default recursion limit (1000).

Examples
--------
>>> sum_linear([1, 2, 3])
(6, 4)
>>> sum_halves(list(range(8)))
(28, 4)
>>> sum_loop([5, 5])
(10, 0)

Constraints
-----------
- 0 <= len(xs) <= 10**6 for the loop and halving versions.

Hints
-----
- Pass depth as a parameter and keep the maximum in a nonlocal variable.
- Base cases for halves: empty range -> 0, one element -> xs[lo].
- Wrap the call in try/except RecursionError.

Follow-ups
----------
- Why is ``sys.setrecursionlimit(10**6)`` not a real fix? (The C stack can still
  overflow and crash the interpreter; convert to an explicit stack instead.)
- What is the space of merge sort? O(n) buffers + O(log n) stack (→ §22.6).
"""
from __future__ import annotations


def sum_linear(xs: list[int]) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def sum_halves(xs: list[int]) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def sum_loop(xs: list[int]) -> tuple[int, int]:
    raise NotImplementedError("TODO")


def hits_recursion_limit(fn, n: int) -> bool:
    raise NotImplementedError("TODO")


def main() -> None:
    for n in (0, 1, 8, 100, 900):
        xs = list(range(n))
        results = [f(xs) for f in (sum_linear, sum_halves, sum_loop)]
        assert len({total for total, _ in results}) == 1
        depths = [d for _, d in results]
        print(f"n={n:<4} sum={results[0][0]:<6} depth linear={depths[0]:<4} "
              f"halves={depths[1]:<3} loop={depths[2]}")
    for fn in (sum_linear, sum_halves, sum_loop):
        print(f"{fn.__name__:<10} n=5000 raises RecursionError: {hits_recursion_limit(fn, 5000)}")
    print("sum_halves depth at n=10**6:", sum_halves(list(range(10**6)))[1])


if __name__ == "__main__":
    main()
