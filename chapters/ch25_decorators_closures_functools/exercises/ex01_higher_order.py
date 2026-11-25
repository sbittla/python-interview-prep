"""
Exercise 01 — Functions as Values: compose, apply_n, dispatch table      [Tier: ★ Core]
Chapter 25 · Pattern: first-class / higher-order functions · Target time: 15 min

Problem
-------
Functions are ordinary objects: you can store them in containers, pass them in
and return them. Implement:

1. `compose(*funcs)` — returns g with g(x) == f1(f2(...fk(x))) (right to left,
   like maths). `compose()` with no functions is the identity.
2. `pipeline(*funcs)` — the same, left to right (Unix-pipe order).
3. `apply_n(f, n)` — returns a function that applies f n times (n >= 0).
4. `run_commands(lines)` — each line is "<op> <int> [<int>]" with ops
   add, sub, mul, neg, abs. Return the list of results; an unknown op gives the
   string "error: unknown op '<op>'". Use a dict of functions (a dispatch table),
   not an if/elif chain.

Examples
--------
>>> compose(str, abs)(-7)
'7'
>>> pipeline(abs, str)(-7)
'7'
>>> apply_n(lambda x: x * 2, 3)(1)
8
>>> run_commands(["add 2 3", "neg 4", "pow 2 3"])
[5, -4, "error: unknown op 'pow'"]

Constraints
-----------
- 0 <= n <= 10**4 for apply_n; each command has the right arity for its op.

Hints
-----
- `functools.reduce` folds a list of functions into one.
- `operator.add`, `operator.neg`, ... are ready-made functions.
- `table.get(op)` returns None for an unknown op: no try/except needed.

Follow-ups
----------
- Make `compose` raise a clear error if any argument is not callable.
- Register new ops with a decorator (`@op("pow")`) — see ex08's registry.
- Why does `sorted(words, key=len)` count as a higher-order call?
"""
from __future__ import annotations

import operator
from functools import reduce
from typing import Callable

TABLE: dict[str, Callable[..., int]] = {
    "add": operator.add,
    "sub": operator.sub,
    "mul": operator.mul,
    "neg": operator.neg,
    "abs": abs,
}


def compose(*funcs: Callable) -> Callable:
    raise NotImplementedError("TODO")


def pipeline(*funcs: Callable) -> Callable:
    raise NotImplementedError("TODO")


def apply_n(f: Callable, n: int) -> Callable:
    raise NotImplementedError("TODO")


def brute_force_run(lines: list[str]) -> list[int | str]:
    raise NotImplementedError("TODO")


def run_commands(lines: list[str]) -> list[int | str]:
    raise NotImplementedError("TODO")


def main() -> None:
    shout = pipeline(str.strip, str.upper, lambda s: s + "!")
    print("pipeline:", shout("  hi there "))
    print("compose(str, abs)(-7) =", repr(compose(str, abs)(-7)))
    print("compose()(42) =", compose()(42))
    print("apply_n(double, 10)(1) =", apply_n(lambda x: 2 * x, 10)(1))
    lines = ["add 2 3", "sub 2 9", "mul 4 5", "neg 4", "abs -6", "pow 2 3"]
    print("dispatch:", run_commands(lines))
    print("same as if/elif:", run_commands(lines) == brute_force_run(lines))
    print("functions are objects:", [f.__name__ for f in (len, abs, compose)])


if __name__ == "__main__":
    main()
