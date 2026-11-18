"""
Exercise 04 — Shopping Carts That Share Items           [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (references) · Target time: 5 min

Problem
-------
Each `Cart` must keep its own list of items. The buggy version declares
`items = []` in the class body, which creates ONE list stored on the class and
shared by every instance, so adding to one cart "adds" to all of them.

Examples
--------
>>> a, b = Cart(), Cart()
>>> a.add("apple")
>>> a.items, b.items
(['apple'], [])

Constraints
-----------
- `add` appends one item; `total_items` returns the count for that cart only.
- A class-wide counter of all carts created (`Cart.created`) IS meant to be shared.

Approach ladder
---------------
1. Buggy  — mutable class attribute: `self.items.append(...)` finds `items` on
   the class (attribute lookup falls back from instance to class) and mutates it.
2. Fixed  — create per-instance state in `__init__`: `self.items = []`.
3. Alternative — `@dataclass` with `field(default_factory=list)` (a bare `= []`
   default is rejected by dataclasses with a ValueError, precisely to stop this bug).

Follow-ups
----------
- Why does `self.count += 1` on an int class attribute NOT have this bug?
  (It rebinds a new instance attribute; ints are immutable.)
- Show where each attribute lives: `vars(a)` vs `vars(Cart)`.
"""
from __future__ import annotations


class BuggyCart:
    items: list[str] = []          # one list, shared by every instance

    def add(self, item: str) -> None:
        self.items.append(item)

    def total_items(self) -> int:
        return len(self.items)


class Cart:
    created = 0                    # intentionally class-wide (immutable int, rebound)

    def __init__(self) -> None:
        self.items: list[str] = []  # per-instance list
        Cart.created += 1

    def add(self, item: str) -> None:
        self.items.append(item)

    def total_items(self) -> int:
        return len(self.items)


def main() -> None:
    a, b = BuggyCart(), BuggyCart()
    a.add("apple")
    print("buggy: a.items =", a.items, "| b.items =", b.items)
    print("buggy: 'items' in vars(a)?", "items" in vars(a))

    a, b = Cart(), Cart()
    a.add("apple")
    print("fixed: a.items =", a.items, "| b.items =", b.items)
    print("fixed: 'items' in vars(a)?", "items" in vars(a))
    print("fixed: carts created =", Cart.created)


if __name__ == "__main__":
    main()
