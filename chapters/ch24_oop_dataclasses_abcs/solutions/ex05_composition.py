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

Approach ladder
---------------
1. Brute force — subclass `list`, override `append`: O(1) appends, but the count is
   wrong for every other way to add items, and the class inherits ~40 methods you never
   vetted (`sort`, `remove`, slice assignment...).
   Overriding every mutator patches it, but you must chase each entry point
   (`__iadd__`, slice `__setitem__`, ...) forever.
2. Optimal    — composition: a private list plus only the methods you choose to expose,
   each a one-line delegation that updates the count. Same complexity, and the public
   surface is exactly what you wrote.

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
        super().__init__(*args)
        self.added = len(self)

    def append(self, x: Any) -> None:
        self.added += 1
        super().append(x)


class AuditedList:
    def __init__(self, items: Iterable[Any] = ()) -> None:
        self._items: list[Any] = []       # has-a list, not is-a list
        self.added = 0
        self.extend(items)

    def append(self, x: Any) -> None:
        self._items.append(x)
        self.added += 1

    def extend(self, items: Iterable[Any]) -> None:
        for x in items:
            self.append(x)

    def insert(self, i: int, x: Any) -> None:
        self._items.insert(i, x)
        self.added += 1

    def __iadd__(self, items: Iterable[Any]) -> AuditedList:
        self.extend(items)
        return self                       # += must return the object

    def pop(self, i: int = -1) -> Any:
        return self._items.pop(i)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._items)

    def __getitem__(self, i: int) -> Any:
        return self._items[i]

    def __repr__(self) -> str:
        return f"AuditedList({self._items!r}, added={self.added})"


class Stack:
    def __init__(self) -> None:
        self._data: list[Any] = []

    def push(self, x: Any) -> None:
        self._data.append(x)

    def pop(self) -> Any:
        if not self._data:
            raise IndexError("empty stack")
        return self._data.pop()

    def peek(self) -> Any:
        if not self._data:
            raise IndexError("empty stack")
        return self._data[-1]

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)


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
