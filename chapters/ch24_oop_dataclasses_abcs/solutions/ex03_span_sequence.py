"""
Exercise 03 — Span: Rebuild range() with the Sequence Protocol  [Tier: ★ Core]
Chapter 24 · Pattern: sequence protocol (__len__, __getitem__, __contains__) · Target time: 25 min

Problem
-------
Implement `Span(start, stop, step=1)`, a lazy arithmetic progression that behaves like
the built-in `range` without storing its elements (`step == 0` -> `ValueError`).

- `len(s)` — number of elements, computed in O(1).
- `s[i]` — supports negative indices; out of range -> `IndexError`.
- `s[a:b:c]` — returns another `Span` (never a list), like `range(10)[2:8:2]`.
- `x in s` — O(1) arithmetic test, not a scan.
- `iter(s)` and `reversed(s)` — lazy generators.
- `s == t` — two spans are equal when they produce the same sequence
  (`Span(0, 0) == Span(5, 5)`; `Span(0, 3, 5) == Span(0, 1)`).
- `repr` -> `Span(0, 10, 2)`.

Examples
--------
>>> s = Span(0, 10, 3); len(s), list(s), s[-1], 9 in s, 4 in s
(4, [0, 3, 6, 9], 9, True, False)
>>> Span(0, 20, 2)[1:8:3]
Span(2, 16, 6)

Constraints
-----------
- |start|, |stop|, |step| up to 10**18: anything O(n) in the length is too slow.

Approach ladder
---------------
1. Brute force — materialise `list(range(...))` in `__init__`; every dunder delegates to
   the list: O(n) time and memory to build, O(n) for `in`.
2. Improved   — keep (start, stop, step) but implement `__contains__`/`__len__` by
   iterating: O(1) memory, still O(n) per query.
3. Optimal    — arithmetic: len = max(0, ceil((stop - start) / step)); element i is
   start + i*step; `x in s` checks bounds and `(x - start) % step == 0`; slicing maps
   through `slice.indices(len)`. O(1) per operation, O(1) memory.

Hints
-----
- Use integer ceiling division `-((start - stop) // step)` to avoid floats.
- `slice(a, b, c).indices(n)` clamps a slice to a length-n sequence and returns
  `(start, stop, step)` in index space; map index space back to values.
- Equality: compare lengths, then first element and (when len > 1) the step.

Follow-ups
----------
- Why does defining only `__getitem__` make a class iterable? (the legacy protocol calls
  it with 0, 1, 2, ... until `IndexError`.)
- Make `Span` hashable consistently with your `__eq__`.
"""
from __future__ import annotations

from collections.abc import Iterator


class ListSpan:
    """Rung 1: materialises every element."""

    def __init__(self, start: int, stop: int, step: int = 1) -> None:
        self.items = list(range(start, stop, step))

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, i: int) -> int:
        return self.items[i]

    def __contains__(self, x: int) -> bool:
        return x in self.items                       # O(n) scan


class Span:
    def __init__(self, start: int, stop: int, step: int = 1) -> None:
        if step == 0:
            raise ValueError("step must not be zero")
        self.start, self.stop, self.step = start, stop, step

    def __len__(self) -> int:
        return max(0, -((self.start - self.stop) // self.step))   # ceil division

    def __getitem__(self, key: int | slice) -> int | Span:
        n = len(self)
        if isinstance(key, slice):
            i, j, k = key.indices(n)                 # clamp to index space
            return Span(self.start + i * self.step,
                        self.start + j * self.step, self.step * k)
        if key < 0:
            key += n
        if not 0 <= key < n:
            raise IndexError("Span index out of range")
        return self.start + key * self.step

    def __contains__(self, x: object) -> bool:
        if not isinstance(x, int) or len(self) == 0:
            return False
        last = self.start + (len(self) - 1) * self.step
        lo, hi = min(self.start, last), max(self.start, last)
        return lo <= x <= hi and (x - self.start) % self.step == 0

    def __iter__(self) -> Iterator[int]:
        for i in range(len(self)):
            yield self.start + i * self.step

    def __reversed__(self) -> Iterator[int]:
        for i in range(len(self) - 1, -1, -1):
            yield self.start + i * self.step

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Span):
            return NotImplemented
        n = len(self)
        if n != len(other):
            return False
        if n == 0:
            return True
        return self[0] == other[0] and (n == 1 or self.step == other.step)

    def __hash__(self) -> int:                       # consistent with __eq__
        n = len(self)
        return hash((n, self[0] if n else None, self.step if n > 1 else None))

    def __repr__(self) -> str:
        return f"Span({self.start}, {self.stop}, {self.step})"


def main() -> None:
    s = Span(0, 10, 3)
    print(s, "len", len(s), "items", list(s), "s[-1] =", s[-1])
    print("9 in s:", 9 in s, "| 4 in s:", 4 in s, "| reversed:", list(reversed(s)))
    print("Span(0, 20, 2)[1:8:3] =", Span(0, 20, 2)[1:8:3],
          "-> range agrees:", list(Span(0, 20, 2)[1:8:3]) == list(range(0, 20, 2)[1:8:3]))
    d = Span(10, -1, -4)
    print(d, "->", list(d), "| d[::-1] ->", list(d[::-1]), "| 2 in d:", 2 in d)
    print("Span(0,0) == Span(5,5):", Span(0, 0) == Span(5, 5),
          "| Span(0,3,5) == Span(0,1):", Span(0, 3, 5) == Span(0, 1))
    big = Span(0, 10**18, 7)
    print("huge span: len", len(big), "| 7*10**16 in big:", 7 * 10**16 in big)
    print("ListSpan agrees on 9:", 9 in ListSpan(0, 10, 3))
    try:
        s[4]
    except IndexError as exc:
        print("IndexError:", exc)


if __name__ == "__main__":
    main()
