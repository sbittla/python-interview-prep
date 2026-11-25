"""
Exercise 04 — Inheritance, super() and the C3 MRO  [Tier: ★ Core]
Chapter 24 · Pattern: cooperative super(), C3 linearisation · Target time: 30 min

Problem
-------
Part A. The classes `Base`, `Left(Base)`, `Right(Base)` and `Child(Left, Right)` below form
a diamond. Every `__init__` appends its class name to a shared `log` list and calls
`super().__init__(log)`. Write `init_order()` that builds a `Child` and returns the log.
Explain why `Base` runs exactly once.

Part B. Implement `c3_linearize(cls, bases)` where `bases` maps every class name to the
list of its direct base names (in declaration order; roots map to `[]`). Return the
method resolution order of `cls` as a list of names, exactly as Python would compute it
(without the implicit `object`). If no consistent order exists, raise `ValueError`.

    L[C] = C + merge(L[B1], ..., L[Bn], [B1, ..., Bn])
    merge: repeatedly take the first head that appears in no list's TAIL; remove it
    from the front of every list; fail if no list head qualifies.

Examples
--------
>>> init_order()
['Child', 'Left', 'Right', 'Base']
>>> c3_linearize("D", {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]})
['D', 'B', 'C', 'A']
>>> c3_linearize("Z", {"X": [], "Y": ["X"], "Z": ["X", "Y"]})
Traceback (most recent call last):
ValueError: inconsistent hierarchy: cannot order ['X'], ['Y', 'X'], ['X', 'Y']

Constraints
-----------
- Up to a few hundred classes; acyclic `bases`.

Hints
-----
- Precompute each class's linearisation recursively (memoise with a dict).
- A candidate head is "good" if it is not in `lst[1:]` for any remaining list.
- Test against Python itself: build classes with `type(name, bases, {})` and read
  `__mro__`.

Follow-ups
----------
- What does `super()` mean in `Left.__init__` when `self` is a `Child`? ("next class after
  Left in type(self).__mro__", which is `Right`, a class `Left` has never heard of.)
- Why must every cooperative `__init__` accept and forward `**kwargs`?
"""
from __future__ import annotations


class Base:
    def __init__(self, log: list[str]) -> None:  # given
        log.append("Base")


class Left(Base):
    def __init__(self, log: list[str]) -> None:  # given
        log.append("Left")
        super().__init__(log)          # next in type(self).__mro__, not "my parent"


class Right(Base):
    def __init__(self, log: list[str]) -> None:  # given
        log.append("Right")
        super().__init__(log)


class Child(Left, Right):
    def __init__(self, log: list[str]) -> None:  # given
        log.append("Child")
        super().__init__(log)


def init_order() -> list[str]:
    raise NotImplementedError("TODO")


def dfs_first_visit(cls: str, bases: dict[str, list[str]]) -> list[str]:
    """Rung 1: depth-first, left-to-right, keep the first visit (wrong on diamonds)."""
    raise NotImplementedError("TODO")


def dfs_last_visit(cls: str, bases: dict[str, list[str]]) -> list[str]:
    """Rung 2: depth-first, keep the LAST visit (breaks local precedence order)."""
    raise NotImplementedError("TODO")


def c3_linearize(cls: str, bases: dict[str, list[str]],
                 memo: dict[str, list[str]] | None = None) -> list[str]:
    raise NotImplementedError("TODO")


def python_mro(cls: str, bases: dict[str, list[str]]) -> list[str]:  # given
    """Ask CPython: build real classes with type() and read __mro__."""
    built: dict[str, type] = {}

    def build(name: str) -> type:
        if name not in built:
            parents = tuple(build(b) for b in bases[name]) or (object,)
            built[name] = type(name, parents, {})
        return built[name]

    return [k.__name__ for k in build(cls).__mro__ if k is not object]


def main() -> None:
    print("init order:", init_order())
    print("Child.__mro__:", [k.__name__ for k in Child.__mro__])
    diamond = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
    print("diamond DFS first-visit:", dfs_first_visit("D", diamond))
    print("diamond C3             :", c3_linearize("D", diamond))
    wiki = {"O": [], "A": ["O"], "B": ["O"], "C": ["O"], "D": ["O"], "E": ["O"],
            "K1": ["A", "B", "C"], "K2": ["D", "B", "E"], "K3": ["D", "A"],
            "Z": ["K1", "K2", "K3"]}
    print("Z last-visit:", dfs_last_visit("Z", wiki))
    print("Z C3        :", c3_linearize("Z", wiki))
    print("Z Python    :", python_mro("Z", wiki))
    bad = {"X": [], "Y": ["X"], "Z": ["X", "Y"]}
    print("inconsistent, last-visit returns:", dfs_last_visit("Z", bad))
    try:
        c3_linearize("Z", bad)
    except ValueError as exc:
        print("ValueError:", exc)
    try:
        python_mro("Z", bad)
    except TypeError as exc:
        print("Python agrees -> TypeError:", exc)


if __name__ == "__main__":
    main()
