"""
Exercise 09 — functools Toolkit: partial, singledispatch, total_ordering  [Tier: ★ Core]
Chapter 25 · Pattern: standard-library higher-order tools · Target time: 25 min

Problem
-------
1. `make_parsers()` returns a dict {"bin": f, "hex": g} where each value is a
   `functools.partial` of `int` with the right `base` ("101" -> 5, "ff" -> 255).
2. `describe(obj)` — a `functools.singledispatch` generic function:
     int  -> "int 5"          bool -> "bool True"   (bool must NOT fall to int)
     str  -> "str of length 3"
     list -> "list [int 1, str of length 1]" (describe each element, recursive)
     dict -> "dict with keys ['a', 'b']" (keys sorted by repr)
     anything else -> "object of type <name>"
3. `Version` — parsed from "1.10.2"; compares numerically by its parts
   (1.10.0 > 1.9.9; "1.2" == "1.2.0"). Define only `__eq__` and `__lt__` and
   let `functools.total_ordering` derive <=, >, >=. Comparing with a non-Version
   returns NotImplemented. `__hash__` must agree with `__eq__`.

Examples
--------
>>> make_parsers()["hex"]("ff")
255
>>> describe([1, "a"])
'list [int 1, str of length 1]'
>>> Version("1.10") > Version("1.9.9"), Version("1.2") == Version("1.2.0")
(True, True)

Constraints
-----------
- Version strings are dot-separated non-negative integers.

Hints
-----
- `@describe.register` reads the type from the first parameter's annotation
  (3.7+); `@describe.register(list)` also works. Union types such as
  `int | float` in register need Python 3.11+.
- Normalise trailing zeros: (1, 2, 0) -> (1, 2), so equal versions hash equally.
- string comparison would say "1.10" < "1.9": compare tuples of ints.

Follow-ups
----------
- singledispatchmethod (3.8+) for methods; dispatch on the first non-self argument.
- total_ordering's derived methods are slower than hand-written ones (an extra
  Python-level call); for hot sort keys use a key function instead.
- Why must `__lt__` return NotImplemented, not False, for foreign types?
"""
from __future__ import annotations

from functools import partial, singledispatch, total_ordering


def make_parsers() -> dict[str, partial]:
    raise NotImplementedError("TODO")


@singledispatch
def describe(obj: object) -> str:
    raise NotImplementedError("TODO")


@describe.register
def _(obj: int) -> str:
    raise NotImplementedError("TODO")


@describe.register
def _(obj: bool) -> str:
    raise NotImplementedError("TODO")


@describe.register
def _(obj: str) -> str:
    raise NotImplementedError("TODO")


@describe.register
def _(obj: list) -> str:
    raise NotImplementedError("TODO")


@describe.register
def _(obj: dict) -> str:
    raise NotImplementedError("TODO")


@total_ordering
class Version:
    def __init__(self, text: str) -> None:
        raise NotImplementedError("TODO")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("TODO")

    def __lt__(self, other: object) -> bool:
        raise NotImplementedError("TODO")

    def __hash__(self) -> int:
        raise NotImplementedError("TODO")

    def __repr__(self) -> str:
        raise NotImplementedError("TODO")


def main() -> None:
    parsers = make_parsers()
    to_bin = parsers["bin"]
    print("partial:", to_bin("101"), parsers["hex"]("ff"), "|", to_bin.func.__name__, to_bin.keywords)
    for obj in (5, True, "abc", [1, "a", [False]], {"b": 1, "a": 2}, 2.5, None):
        print(f"describe({obj!r}) -> {describe(obj)}")
    print("registered types:", sorted(t.__name__ for t in describe.registry))
    vs = [Version(s) for s in ("1.10", "1.9.9", "1.2.0", "1.2", "0.9")]
    print("sorted:", sorted(vs))
    print("1.10 > 1.9.9:", Version("1.10") > Version("1.9.9"),
          "| string compare says:", "1.10" > "1.9.9")
    print("1.2 == 1.2.0:", Version("1.2") == Version("1.2.0"),
          "| >= derived:", Version("1.2") >= Version("1.2.0"),
          "| distinct in a set:", len(set(vs)))
    try:
        Version("1.0") < "2.0"
    except TypeError as exc:
        print("foreign type:", exc)


if __name__ == "__main__":
    main()
