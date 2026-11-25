"""
Exercise 07 — Inventory with Dataclasses: field, frozen, order, slots  [Tier: ★ Core]
Chapter 24 · Pattern: @dataclass options, __post_init__, replace, asdict · Target time: 25 min

Problem
-------
Model a small warehouse with dataclasses (Python 3.10+: `slots=True` needs 3.10).

1. `Version(major, minor=0, patch=0)` — frozen and ordered, so versions sort numerically
   (1.10 > 1.9) and can be set members / dict keys. `Version.parse("1.10.2")` accepts 1–3
   dot-separated non-negative ints; `str(v)` -> `"1.10.2"`.
2. `Location(aisle, shelf)` — frozen with slots; used as a dict key.
3. `Item(name, price_cents, qty=0, location=None)` — frozen with slots;
   `__post_init__` rejects an empty name and negative price or qty (`ValueError`).
   `item.value` (a property) is `price_cents * qty`.
4. `Cart(owner, items=[])` — MUTABLE; each cart must get its own list
   (`field(default_factory=list)`); `cart.add(item)` appends, `cart.total` sums values.
5. Functions:
   - `restock(item, n)` returns a NEW item with `qty + n` (`dataclasses.replace`).
   - `by_location(items)` -> `{Location: sorted item names}` (items with no location skipped).
   - `report(items)` -> list of `asdict(item)` dicts sorted by value desc, then name.

Examples
--------
>>> [str(v) for v in sorted([Version.parse("1.10"), Version.parse("1.9"), Version(1)])]
['1.0.0', '1.9.0', '1.10.0']
>>> restock(Item("bolt", 5, 10), 5).qty
15

Constraints
-----------
- Up to 10**5 items; `report` O(n log n), `by_location` O(n log n), the rest O(1).

Hints
-----
- `order=True` compares instances as tuples of their fields IN DECLARATION ORDER.
- A frozen dataclass's `__post_init__` may read fields freely; to set a derived field
  you would need `object.__setattr__(self, name, value)`.
- `field(default=[])` raises `ValueError` at class-creation time; use `default_factory`.

Follow-ups
----------
- `eq=True, frozen=False` (the default) sets `__hash__` to None: plain dataclasses are
  unhashable. Why is that the right default?
- When would you choose `NamedTuple` instead? (tuple unpacking, immutability, and the
  record must also BE a tuple.)
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int = 0
    patch: int = 0

    @classmethod
    def parse(cls, text: str) -> Version:
        raise NotImplementedError("TODO")

    def __str__(self) -> str:
        raise NotImplementedError("TODO")


@dataclass(frozen=True, slots=True)        # slots=True: Python 3.10+
class Location:
    aisle: str
    shelf: int


@dataclass(frozen=True, slots=True)
class Item:
    name: str
    price_cents: int
    qty: int = 0
    location: Location | None = None

    def __post_init__(self) -> None:
        raise NotImplementedError("TODO")

    @property
    def value(self) -> int:
        raise NotImplementedError("TODO")


@dataclass
class Cart:
    owner: str
    items: list[Item] = field(default_factory=list)   # fresh list per Cart

    def add(self, item: Item) -> None:
        raise NotImplementedError("TODO")

    @property
    def total(self) -> int:
        raise NotImplementedError("TODO")


class HandItem:
    """Rung 2: the boilerplate @dataclass writes for you."""

    def __init__(self, name: str, price_cents: int, qty: int = 0) -> None:
        raise NotImplementedError("TODO")

    def __repr__(self) -> str:
        raise NotImplementedError("TODO")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("TODO")

    def __hash__(self) -> int:
        raise NotImplementedError("TODO")


def restock(item: Item, n: int) -> Item:
    raise NotImplementedError("TODO")


def by_location(items: list[Item]) -> dict[Location, list[str]]:
    raise NotImplementedError("TODO")


def report(items: list[Item]) -> list[dict]:
    raise NotImplementedError("TODO")


def main() -> None:
    vs = [Version.parse(s) for s in ["1.10", "1.9.3", "2", "1.9"]]
    print("sorted versions:", [str(v) for v in sorted(vs)],
          "| as strings:", sorted(["1.10", "1.9.3", "2", "1.9"]))
    print("hashable:", len({Version(1), Version.parse("1.0.0")}))
    a1 = Location("A", 1)
    items = [Item("bolt", 5, 100, a1), Item("nut", 3, 100, a1),
             Item("drill", 4999, 2, Location("B", 3)), Item("glue", 250, 4)]
    print(items[2])
    print("by_location:", by_location(items))
    for row in report(items)[:2]:
        print("report row:", row)
    cart1, cart2 = Cart("ada"), Cart("bob")
    cart1.add(items[0])
    print("carts:", len(cart1.items), len(cart2.items), "| cart1 total:", cart1.total)
    bolt = restock(items[0], 50)
    print("restocked:", bolt.qty, "| original:", items[0].qty)
    try:
        items[0].qty = 0
    except AttributeError as exc:
        print(type(exc).__name__, "is AttributeError:", isinstance(exc, AttributeError))
    print("slots -> no __dict__:", not hasattr(items[0], "__dict__"),
          "| Cart hashable:", Cart.__hash__ is not None)
    try:
        @dataclass
        class Bad:
            tags: list = []
    except ValueError as exc:
        print("ValueError:", exc)
    try:
        Item("", 1)
    except ValueError as exc:
        print("ValueError:", exc)
    print("HandItem == equivalent:", HandItem("bolt", 5, 1) == HandItem("bolt", 5, 1))


if __name__ == "__main__":
    main()
