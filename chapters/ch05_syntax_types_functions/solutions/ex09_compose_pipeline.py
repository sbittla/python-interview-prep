"""
Exercise 09 — Compose Functions Into a Pipeline               [Tier: ★ Core]
Chapter 05 · Pattern: first-class functions, lambdas · Target time: 15 min

Problem
-------
Functions are values: they can be stored, passed and returned. Implement

- ``compose(*funcs)`` returning a function that applies ``funcs`` right-to-left
  (``compose(f, g)(x) == f(g(x))``),
- ``solve(*funcs)`` (a "pipeline") applying them left-to-right
  (``solve(f, g)(x) == g(f(x))``).

With no functions, both return the identity function. Then use your pipeline with lambdas to
normalise messy user names.

Examples
--------
>>> inc = lambda x: x + 1; dbl = lambda x: x * 2
>>> compose(inc, dbl)(5), solve(inc, dbl)(5)
(11, 12)
>>> solve()(42)
42

Constraints
-----------
- every function takes exactly one argument

Approach ladder
---------------
1. Brute force — write a new wrapper function by hand for every combination you need. O(1)
   per call but no reuse.
2. Optimal    — return a closure that loops over the stored tuple of functions. Building is
   O(k); each call is O(k) function applications. ``functools.reduce`` gives a one-liner
   (Chapter 6), but the loop is easier to explain and debug.

Follow-ups
----------
- Why does ``[lambda: i for i in range(3)]`` return 2 three times? Late binding (Chapter 7).
- How would you support functions with several arguments? Make the first stage take ``*args``.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

Fn = Callable[[Any], Any]


def brute_force_normalise(name: str) -> str:
    return " ".join(name.strip().split()).title()


def compose(*funcs: Fn) -> Fn:
    def composed(x: Any) -> Any:
        for f in reversed(funcs):
            x = f(x)
        return x
    return composed


def solve(*funcs: Fn) -> Fn:
    def piped(x: Any) -> Any:
        for f in funcs:
            x = f(x)
        return x
    return piped


def main() -> None:
    inc = lambda x: x + 1      # noqa: E731  (lambdas bound to names only for the demo)
    dbl = lambda x: x * 2      # noqa: E731
    print("compose(inc, dbl)(5) =", compose(inc, dbl)(5))
    print("pipeline(inc, dbl)(5) =", solve(inc, dbl)(5))
    print("identity:", solve()(42), compose()("same"))

    normalise = solve(str.strip, str.split, " ".join, str.title)   # methods are functions too
    raw = ["  ada   lovelace ", "GRACE hopper", "\tlinus  torvalds\n"]
    print([normalise(n) for n in raw])
    print("brute agrees:", [brute_force_normalise(n) for n in raw] == [normalise(n) for n in raw])

    ops = {"square": lambda x: x * x, "neg": lambda x: -x, "abs": abs}   # dispatch table
    print({name: f(-3) for name, f in sorted(ops.items())})
    print("sorted by last name:", sorted(map(normalise, raw), key=lambda n: n.split()[-1]))


if __name__ == "__main__":
    main()
