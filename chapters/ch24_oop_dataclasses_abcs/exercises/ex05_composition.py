"""
Exercise 05 — Composition over Inheritance: an Audited List and a Strict Stack  [Tier: ★ Core]
Chapter 24 · Pattern: wrap-and-delegate instead of subclassing built-ins · Target time: 20 min

Problem
-------
1. `AuditedList` counts how many items were EVER added (`added`), however they arrive:
   `append(x)`, `extend(iterable)`, `insert(i, x)` and `+=`. It supports `len`,
   iteration, indexing, `pop()` (which does not change `added`) and `repr` ->
   `AuditedList([1, 2], added=3)`. Build it by COMPOSITION: hold a list, do not
   subclass it.
2. `InheritedAuditList(list)` is the tempting rung: it subclasses `list` and overrides
   only `append`. Show (in `main` and the tests) that `extend`, `insert` and `+=` bypass
   the count, because `list`'s C methods never call your `append`.
3. `Stack` exposes ONLY `push`, `pop`, `peek`, `__len__`, `__bool__` by wrapping a list,
   so callers cannot `insert(0, x)` or index into the middle. `pop`/`peek` on an empty
   stack raise `IndexError("empty stack")`.

Examples
--------
>>> a = AuditedList(); a.append(1); a.extend([2, 3]); a.pop(); a
AuditedList([1, 2], added=3)
>>> s = Stack(); s.push("x"); hasattr(s, "insert"), s.peek()
(False, 'x')

Constraints
-----------
- `append`, `pop`, `push`, `peek` amortised O(1); `extend` O(k); `insert` O(n).

Hints
-----
- `__iadd__` must `return self`, or `a += [4]` rebinds `a` to whatever you returned.
- If every mutation must pass through your hooks, subclass
  `collections.abc.MutableSequence`: implement `__getitem__`, `__setitem__`, `__delitem__`,
  `__len__` and `insert`, and its mixin `append`, `extend` and `+=` all call your `insert`.
  `collections.UserList` does NOT help here: its `extend` calls `self.data.extend` directly,
  so an overridden `append` is bypassed just as with `list`.

Follow-ups
----------
- When is inheritance the right call? A real "is-a" relation whose base class was
  designed for extension (documented hooks, an ABC) — e.g. `Exception` subclasses.
- Delegate the rest automatically with `__getattr__`? It forwards everything, which
  reopens the surface you wanted to close.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any


class InheritedAuditList(list):
    """Rung 1: inheritance. Only append is counted."""

    def __init__(self, *args: Any) -> None:
        raise NotImplementedError("TODO")

    def append(self, x: Any) -> None:
        raise NotImplementedError("TODO")


class AuditedList:
    def __init__(self, items: Iterable[Any] = ()) -> None:
        raise NotImplementedError("TODO")

    def append(self, x: Any) -> None:
        raise NotImplementedError("TODO")

    def extend(self, items: Iterable[Any]) -> None:
        raise NotImplementedError("TODO")

    def insert(self, i: int, x: Any) -> None:
        raise NotImplementedError("TODO")

    def __iadd__(self, items: Iterable[Any]) -> AuditedList:
        raise NotImplementedError("TODO")

    def pop(self, i: int = -1) -> Any:
        raise NotImplementedError("TODO")

    def __len__(self) -> int:
        raise NotImplementedError("TODO")

    def __iter__(self) -> Iterator[Any]:
        raise NotImplementedError("TODO")

    def __getitem__(self, i: int) -> Any:
        raise NotImplementedError("TODO")

    def __repr__(self) -> str:
        raise NotImplementedError("TODO")


class Stack:
    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def push(self, x: Any) -> None:
        raise NotImplementedError("TODO")

    def pop(self) -> Any:
        raise NotImplementedError("TODO")

    def peek(self) -> Any:
        raise NotImplementedError("TODO")

    def __len__(self) -> int:
        raise NotImplementedError("TODO")

    def __bool__(self) -> bool:
        raise NotImplementedError("TODO")


def main() -> None:
    inh = InheritedAuditList()
    comp = AuditedList()
    for target in (inh, comp):
        target.append(1)
        target.extend([2, 3])
        target.insert(0, 0)
        target += [4]
    print("inheritance : len", len(inh), "added", inh.added, "<- extend/insert/+= bypassed")
    print("composition :", comp, "| len", len(comp))
    comp.pop()
    print("after pop   :", comp, "| comp[0] =", comp[0], "| list(comp) =", list(comp))
    s = Stack()
    for ch in "abc":
        s.push(ch)
    print("stack pop:", s.pop(), "| peek:", s.peek(), "| len:", len(s),
          "| has insert:", hasattr(s, "insert"))
    s.pop()
    s.pop()
    print("empty stack is falsy:", not s)
    try:
        s.pop()
    except IndexError as exc:
        print("IndexError:", exc)


if __name__ == "__main__":
    main()
