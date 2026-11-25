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

Approach ladder
---------------
1. Brute force — dicts/tuples: O(1) access, but typos in keys pass silently, tuples
   compare by position with no names, and nothing validates.
2. Improved   — hand-written classes (`HandItem` below): correct, O(1), but ~15 lines of
   `__init__`/`__repr__`/`__eq__` boilerplate per record, easy to let drift out of sync
   when a field is added.
3. Optimal    — `@dataclass`: the generator writes `__init__`, `__repr__`, `__eq__`
   (and `__lt__`... with `order=True`, `__hash__` with `frozen=True`); you add only
   validation in `__post_init__`. Same O(1) costs.

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
        parts = text.split(".")
        if not 1 <= len(parts) <= 3 or not all(p.isascii() and p.isdigit() for p in parts):
            raise ValueError(f"bad version {text!r}")
        return cls(*map(int, parts))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


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
        if not self.name:
            raise ValueError("name must be non-empty")
        if self.price_cents < 0 or self.qty < 0:
            raise ValueError("price and qty must be >= 0")

    @property
    def value(self) -> int:
        return self.price_cents * self.qty


@dataclass
class Cart:
    owner: str
    items: list[Item] = field(default_factory=list)   # fresh list per Cart

    def add(self, item: Item) -> None:
        self.items.append(item)

    @property
    def total(self) -> int:
        return sum(i.value for i in self.items)


class HandItem:
    """Rung 2: the boilerplate @dataclass writes for you."""

    def __init__(self, name: str, price_cents: int, qty: int = 0) -> None:
        if not name or price_cents < 0 or qty < 0:
            raise ValueError("invalid item")
        self.name, self.price_cents, self.qty = name, price_cents, qty

    def __repr__(self) -> str:
        return f"HandItem(name={self.name!r}, price_cents={self.price_cents}, qty={self.qty})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HandItem):
            return NotImplemented
        return (self.name, self.price_cents, self.qty) == (other.name, other.price_cents, other.qty)

    def __hash__(self) -> int:
        return hash((self.name, self.price_cents, self.qty))


def restock(item: Item, n: int) -> Item:
    return replace(item, qty=item.qty + n)            # new object; __post_init__ re-runs


def by_location(items: list[Item]) -> dict[Location, list[str]]:
    out: dict[Location, list[str]] = {}
    for it in items:
        if it.location is not None:
            out.setdefault(it.location, []).append(it.name)
    return {loc: sorted(names) for loc, names in out.items()}


def report(items: list[Item]) -> list[dict]:
    return [asdict(it) for it in sorted(items, key=lambda it: (-it.value, it.name))]


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
