"""
Exercise 12 — Check Arguments Against Type Hints              [Tier: ◆ Extended]
Chapter 05 · Pattern: type hints are metadata, not enforcement · Target time: 20 min

Problem
-------
Python never checks type hints at runtime: ``def f(x: int)`` happily accepts ``"hello"``.
Write ``solve(func, *args, **kwargs)`` that binds the arguments to ``func``'s signature
(applying defaults) and returns a sorted list of messages, one per argument whose value does
not match its annotation, in the form ``"<name>: expected <hint>, got <type name>"``. Rules:

- unannotated parameters are not checked;
- plain classes (``int``, ``str``, user classes) use ``isinstance``;
- ``X | Y`` and ``Optional[X]`` unions pass if any member matches;
- parameterised generics such as ``list[int]`` check only the container (``list``);
- ``bool`` must not satisfy ``int`` (even though ``bool`` subclasses ``int``);
- arguments that cannot be bound raise ``TypeError`` exactly as calling ``func`` would.

Examples
--------
>>> def area(w: int, h: int = 1, label: str | None = None) -> int: return w * h
>>> solve(area, 3, "4")
['h: expected int, got str']
>>> solve(area, 3, 4, label=None)
[]

Constraints
-----------
- annotations may be strings (``from __future__ import annotations``): resolve them with
  ``typing.get_type_hints``

Approach ladder
---------------
1. Brute force — read ``func.__annotations__`` directly and match positional args by index.
   Breaks on keyword arguments, defaults and string annotations.
2. Optimal    — ``inspect.signature(func).bind(*args, **kwargs)`` maps every value to its
   parameter name; ``typing.get_type_hints`` resolves string annotations; ``typing.get_origin``
   and ``get_args`` take generics and unions apart. O(p) for p parameters.

Follow-ups
----------
- Turn it into a decorator that raises on mismatch (Chapter 25).
- In real projects use a static checker (mypy, pyright) or a validation library instead.
"""
from __future__ import annotations

import inspect
import types
import typing
from typing import Any


def _matches(value: Any, hint: Any) -> bool:
    if hint is Any:
        return True
    if hint is None or hint is type(None):
        return value is None
    origin = typing.get_origin(hint)
    if origin is typing.Union or origin is types.UnionType:
        return any(_matches(value, member) for member in typing.get_args(hint))
    if origin is not None:              # list[int] -> list, dict[str, int] -> dict
        return isinstance(value, origin)
    if hint is int and isinstance(value, bool):
        return False
    if hint is float and isinstance(value, int) and not isinstance(value, bool):
        return True                     # the numeric tower: an int is acceptable for float
    return isinstance(value, hint)


def _hint_name(hint: Any) -> str:
    return hint.__name__ if isinstance(hint, type) else str(hint).replace("typing.", "")


def brute_force(func: Any, *args: Any) -> list[str]:
    errors = []
    names = list(inspect.signature(func).parameters)
    for name, value in zip(names, args):
        hint = func.__annotations__.get(name)
        if isinstance(hint, type) and not isinstance(value, hint):
            errors.append(f"{name}: expected {hint.__name__}, got {type(value).__name__}")
    return sorted(errors)


def solve(func: Any, *args: Any, **kwargs: Any) -> list[str]:
    bound = inspect.signature(func).bind(*args, **kwargs)
    bound.apply_defaults()
    hints = typing.get_type_hints(func)
    errors = []
    for name, value in bound.arguments.items():
        if name not in hints:
            continue
        hint = hints[name]
        if not _matches(value, hint):
            errors.append(f"{name}: expected {_hint_name(hint)}, got {type(value).__name__}")
    return sorted(errors)


def area(w: int, h: int = 1, label: str | None = None) -> int:
    return w * h


def mean(xs: list[float], weight: float = 1.0, *, verbose: bool = False) -> float:
    return sum(xs) / len(xs) * weight


def main() -> None:
    print("hints are not enforced:", area("ab", 3))          # runs fine: 'ab' * 3
    print("raw __annotations__   :", area.__annotations__)    # strings, because of the future import
    print("resolved hints        :", {k: _hint_name(v) for k, v in typing.get_type_hints(area).items()})
    print(solve(area, 3, "4"))
    print(solve(area, 3, 4, label=None))
    print(solve(area, True, 2.5, label=7))
    print(solve(mean, (1, 2), weight=2, verbose="yes"))
    print("brute misses string hints:", brute_force(area, 3, "4"))
    try:
        solve(area, 1, 2, 3, 4)
    except TypeError as exc:
        print("TypeError:", exc)


if __name__ == "__main__":
    main()
