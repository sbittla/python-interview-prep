"""
Exercise 03 — Your First Decorator: count_calls and functools.wraps     [Tier: ★ Core]
Chapter 25 · Pattern: decorator = function in, wrapper out · Target time: 15 min

Problem
-------
1. `count_calls(func)` returns a wrapper that forwards every call (any positional
   and keyword arguments) and counts calls in a `calls` attribute on the wrapper.
   The wrapper must keep func's `__name__`, `__doc__` and expose the original as
   `__wrapped__` (use `functools.wraps`).
2. (provided) `count_calls_naive(func)` — the same without `wraps`; compare it
   with yours.
3. `bold(func)` / `italic(func)` wrap a str-returning function's result in
   <b>...</b> / <i>...</i>. Show that stacking applies the BOTTOM decorator first.

Examples
--------
>>> def greet(name): return "hi " + name
>>> g = count_calls(greet)
>>> g("ann"), g(name="bo"), g.calls, g.__name__
('hi ann', 'hi bo', 2, 'greet')
>>> bold(italic(lambda: "x"))()
'<b><i>x</i></b>'

Constraints
-----------
- The wrapper adds O(1) work per call.

Hints
-----
- `@d` above `def f` means `f = d(f)`, run once, at definition time.
- Forward with `*args, **kwargs` and RETURN the result.
- A function can store attributes: `wrapper.calls = 0`.

Follow-ups
----------
- Why does `inspect.signature(g)` show `(name)` and not `(*args, **kwargs)`?
- Reset the counter without re-decorating. Make the counter thread-safe (Ch. 28).
- What is printed if the decorator itself prints at decoration time?
"""
from __future__ import annotations

import inspect
from functools import wraps
from typing import Callable


def count_calls_naive(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


def count_calls(func: Callable) -> Callable:
    raise NotImplementedError("TODO")


def bold(func: Callable[..., str]) -> Callable[..., str]:
    raise NotImplementedError("TODO")


def italic(func: Callable[..., str]) -> Callable[..., str]:
    raise NotImplementedError("TODO")


def main() -> None:
    def greet(name: str, punct: str = "!") -> str:
        """Say hello."""
        return f"hi {name}{punct}"

    naive, good = count_calls_naive(greet), count_calls(greet)
    print(good("ann"), good(name="bo", punct="?"), "| calls =", good.calls)
    print("naive:", naive.__name__, naive.__doc__, inspect.signature(naive))
    print("wraps:", good.__name__, good.__doc__, inspect.signature(good))
    print("original reachable:", good.__wrapped__ is greet, inspect.unwrap(good) is greet)

    @bold
    @italic
    def title() -> str:
        return "Decorators"

    print("stacked:", title(), "| equivalent:", bold(italic(lambda: "Decorators"))())


if __name__ == "__main__":
    main()
