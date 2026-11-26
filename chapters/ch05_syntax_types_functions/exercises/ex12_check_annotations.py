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
- ``bool`` must not satisfy ``int`` (even though ``bool`` subclasses ``int``), but an ``int``
  satisfies ``float`` (the PEP 484 numeric shortcut);
- ``Literal[...]`` passes if the value equals one of the literals *and* has the same type;
- ``*args: T`` / ``**kwargs: T`` annotate each element, so check every element and name it
  ``<param>[i]`` / ``<param>['key']`` in the message (e.g. ``names[1]``);
- ``Any``, type variables and other special forms that ``isinstance`` rejects are not checked;
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

Hints
-----
1. ``brute_force``: match ``func.__annotations__`` to positional arguments by index, and note
   what it gets wrong (keywords, defaults, string annotations).
2. ``solve``: ``inspect.signature(...)`` can bind arguments to parameter names and apply
   defaults; ``typing.get_type_hints`` turns string annotations into objects.
3. ``typing.get_origin`` / ``typing.get_args`` take ``list[int]``, unions and ``Literal``
   apart. ``bool`` is a subclass of ``int``: special-case it.
4. A parameter's ``kind`` tells you whether it is ``*args`` or ``**kwargs``.

Follow-ups
----------
- Turn it into a decorator that raises on mismatch (Chapter 25).
- In real projects use a static checker (mypy, pyright) or a validation library instead.
"""
from __future__ import annotations

import typing
from typing import Any, Literal


def _matches(value: Any, hint: Any) -> bool:
    raise NotImplementedError("TODO")


def _hint_name(hint: Any) -> str:
    raise NotImplementedError("TODO")


def brute_force(func: Any, *args: Any) -> list[str]:
    raise NotImplementedError("TODO")


def solve(func: Any, *args: Any, **kwargs: Any) -> list[str]:
    raise NotImplementedError("TODO")


def area(w: int, h: int = 1, label: str | None = None) -> int:
    return w * h


def mean(xs: list[float], weight: float = 1.0, *, verbose: bool = False) -> float:
    return sum(xs) / len(xs) * weight


def tag(*names: str, mode: Literal["a", "w"] = "a", **meta: int) -> None:
    return None


def main() -> None:
    print("hints are not enforced:", area("ab", 3))          # runs fine: 'ab' * 3
    print("raw __annotations__   :", area.__annotations__)    # strings, because of the future import
    print("resolved hints        :", {k: _hint_name(v) for k, v in typing.get_type_hints(area).items()})
    print(solve(area, 3, "4"))
    print(solve(area, 3, 4, label=None))
    print(solve(area, True, 2.5, label=7))
    print(solve(mean, (1, 2), weight=2, verbose="yes"))
    print(solve(tag, "x", 3, mode="r", size=1, flag=True))
    print("brute misses string hints:", brute_force(area, 3, "4"))
    try:
        solve(area, 1, 2, 3, 4)
    except TypeError as exc:
        print("TypeError:", exc)


if __name__ == "__main__":
    main()
