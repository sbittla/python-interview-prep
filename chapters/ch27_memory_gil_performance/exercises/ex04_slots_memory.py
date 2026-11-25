"""
Exercise 04 — `__slots__`: Measure the Saving, Know the Cost   [Tier: ★ Core]
Chapter 27 · Pattern: comparative memory measurement · Target time: 20 min

Problem
-------
A service keeps a million small `Point(x, y)` records in memory. Compare a
plain class with a `__slots__` class.

1. `peak_bytes(factory, n)` returns the peak traced allocation (tracemalloc)
   while building a list of n objects with `factory(i)`.
2. `compare(n)` returns a dict of booleans:
     "slots smaller"              slotted peak < plain peak
     "saves at least 25%"         slotted peak <= 0.75 * plain peak
3. `behaviour()` returns a dict of booleans describing the trade-offs:
     "plain has __dict__", "slotted has __dict__",
     "slotted rejects new attribute", "slotted weakref-able",
     "dataclass(slots=True) has __dict__".

Examples
--------
>>> compare(20_000)["slots smaller"]
True

Constraints
-----------
- Print only booleans: byte counts differ across versions and platforms.


Hints
-----
- `tracemalloc.start()` / `get_traced_memory()` returns (current, peak).
- `weakref.ref(obj)` raises TypeError unless "__weakref__" is in `__slots__`.

Follow-ups
----------
- What breaks with slots? (No new attributes, no `__dict__`-based tricks like
  `vars(obj)`, multiple inheritance with two non-empty slot layouts fails.)
- For a million points, would a NumPy array or `array('d')` beat both?
  (Yes: no per-object header at all.)
"""
from __future__ import annotations

import tracemalloc
import weakref
from dataclasses import dataclass
from typing import Callable


class Plain:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Slotted:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


@dataclass(slots=True)                  # slots=True needs Python 3.10+
class SlottedData:
    x: int
    y: int


def peak_bytes(factory: Callable[[int], object], n: int) -> int:
    raise NotImplementedError("TODO")


def compare(n: int) -> dict[str, bool]:
    raise NotImplementedError("TODO")


def behaviour() -> dict[str, bool]:
    raise NotImplementedError("TODO")


def main() -> None:
    for claim, ok in compare(50_000).items():
        print(f"{claim}: {ok}")
    for claim, ok in behaviour().items():
        print(f"{claim}: {ok}")


if __name__ == "__main__":
    main()
