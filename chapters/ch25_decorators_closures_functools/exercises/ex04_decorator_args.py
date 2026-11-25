"""
Exercise 04 — Decorators with Arguments: repeat, validate, optional parens  [Tier: ★ Core]
Chapter 25 · Pattern: decorator factory (three nested functions) · Target time: 20 min

Problem
-------
1. `repeat(times)` — `@repeat(3)` makes the function run 3 times per call and
   return the list of results. `times < 0` raises ValueError when the FACTORY is
   called (decoration time), not later.
2. `validate(**checks)` — `@validate(age=lambda v: v >= 0)` checks the named
   parameters on every call, whether passed positionally or by keyword, and
   defaults included. A failing check raises
   ValueError("<func>: invalid <param>=<value!r>"). An unknown parameter name in
   `checks` raises TypeError at decoration time.
3. `tag(func=None, *, name="span")` — usable both as `@tag` and as
   `@tag(name="em")`; wraps a str result in <name>...</name>.

Examples
--------
>>> repeat(2)(lambda: "x")()
['x', 'x']
>>> ok = validate(n=lambda v: v > 0)(lambda n: n * 2); ok(3)
6
>>> tag(lambda: "hi")(), tag(name="em")(lambda: "hi")()
('<span>hi</span>', '<em>hi</em>')

Constraints
-----------
- Wrapped functions may take any mix of positional and keyword arguments.

Hints
-----
- `@repeat(3)` evaluates `repeat(3)` first, then applies the result to the function.
- `sig = inspect.signature(func)`; `bound = sig.bind(*args, **kwargs)`;
  `bound.apply_defaults()`; then read `bound.arguments`.
- Compute the signature once at decoration time, not on every call.

Follow-ups
----------
- Why is `@repeat` (no parentheses) a bug, and what error do you get?
- Make validate read checks from type annotations instead.
- Python 3.9+ allows any expression after @ (PEP 614), e.g. `@handlers["x"]`.
"""
from __future__ import annotations

import inspect
from functools import wraps
from typing import Callable


def repeat(times: int) -> Callable[[Callable], Callable]:
    raise NotImplementedError("TODO")


def validate(**checks: Callable[[object], bool]) -> Callable[[Callable], Callable]:
    raise NotImplementedError("TODO")


def tag(func: Callable | None = None, *, name: str = "span"):
    raise NotImplementedError("TODO")


def main() -> None:
    @repeat(3)
    def roll(face: int) -> int:
        return face

    print("repeat(3):", roll(6), "| name kept:", roll.__name__)
    try:
        repeat(-1)
    except ValueError as exc:
        print("repeat(-1) fails at decoration time:", exc)

    @validate(qty=lambda q: q > 0, unit=lambda u: u in {"kg", "g"})
    def order(item: str, qty: int, unit: str = "kg") -> str:
        return f"{qty}{unit} {item}"

    print("order:", order("rice", 2), "|", order("salt", qty=5, unit="g"))
    for args, kwargs in ((("rice", 0), {}), (("rice", 1), {"unit": "lb"})):
        try:
            order(*args, **kwargs)
        except ValueError as exc:
            print("rejected:", exc)
    try:
        validate(colour=bool)(order)
    except TypeError as exc:
        print("bad check name:", exc)

    @tag
    def plain() -> str:
        return "hi"

    @tag(name="em")
    def emph() -> str:
        return "hi"

    print("tag:", plain(), emph())


if __name__ == "__main__":
    main()
