"""
Exercise 10 — Singleton, Factory, Strategy, Observer in Python  [Tier: ◆ Extended]
Chapter 24 · Pattern: GoF patterns with Python idioms · Target time: 30 min

Problem
-------
1. Singleton — `Config()` always returns the SAME object; `__init__` work (loading the
   defaults `{"debug": False}`) runs only once, so a later `Config()` does not wipe
   settings. `Config.reset()` drops the instance (for tests).
2. Factory — `make_shape(spec)` turns a dict like `{"kind": "circle", "r": 1}` into a
   `Circle`, `Square` or `Rect` object via a registry filled by the `@register("circle")`
   decorator. Unknown kind -> `ValueError` listing the known kinds (sorted). Every shape
   has `area()`.
3. Strategy — `Checkout(pricing)` totals a list of cents with an interchangeable pricing
   strategy: any callable `list[int] -> int`. Provide `no_discount`, `percent_off(p)`
   (a factory returning a strategy; rounds half up to whole cents) and
   `buy_n_get_one(n)` (for every n + 1 items in the cart one is free, and the free ones
   are the cheapest). The strategy can be swapped at runtime.
4. Observer — `EventBus.subscribe(event, handler)` returns an unsubscribe function;
   `publish(event, payload)` calls the handlers for that event in subscription order and
   returns how many ran.

Examples
--------
>>> Config() is Config()
True
>>> Checkout(percent_off(10)).total([1000, 500])
1350

Constraints
-----------
- publish O(h) for h handlers; make_shape O(1); totals O(n log n) for buy_n_get_one.

Hints
-----
- In `__new__`, create the instance once and store it on the class; guard `__init__`
  with an `_initialised` flag, because Python calls `__init__` on every `Config()`.
- The simplest singleton in Python is a module: modules are imported once per process.
- `subscribe` can return `lambda: handlers.remove(handler)`.

Follow-ups
----------
- Why do many Python reviewers object to Singleton? (hidden global state; hard to test.
  Prefer passing a config object in.)
- Thread-safe singleton: double-checked locking with `threading.Lock` (→ Ch 28).
- Observer with weak references so subscribers can be garbage-collected (`weakref`).
"""
from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Callable
from typing import Any


# --- Singleton ---------------------------------------------------------------
class Config:
    _instance: Config | None = None

    def __new__(cls) -> Config:
        raise NotImplementedError("TODO")

    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    @classmethod
    def reset(cls) -> None:
        raise NotImplementedError("TODO")


# --- Factory -----------------------------------------------------------------
SHAPES: dict[str, type] = {}


def register(kind: str) -> Callable[[type], type]:  # given
    def deco(cls: type) -> type:
        SHAPES[kind] = cls
        return cls
    return deco


@register("circle")
class Circle:
    def __init__(self, r: float) -> None:
        raise NotImplementedError("TODO")

    def area(self) -> float:
        raise NotImplementedError("TODO")


@register("square")
class Square:
    def __init__(self, side: float) -> None:
        raise NotImplementedError("TODO")

    def area(self) -> float:
        raise NotImplementedError("TODO")


@register("rect")
class Rect:
    def __init__(self, w: float, h: float) -> None:
        raise NotImplementedError("TODO")

    def area(self) -> float:
        raise NotImplementedError("TODO")


def make_shape(spec: dict[str, Any]) -> Any:
    raise NotImplementedError("TODO")


def make_shape_if_chain(spec: dict[str, Any]) -> Any:
    """Rung 1: every new shape edits this function."""
    raise NotImplementedError("TODO")


# --- Strategy ----------------------------------------------------------------
Pricing = Callable[[list[int]], int]


def no_discount(prices: list[int]) -> int:
    raise NotImplementedError("TODO")


def percent_off(p: int) -> Pricing:
    raise NotImplementedError("TODO")


def buy_n_get_one(n: int) -> Pricing:
    raise NotImplementedError("TODO")


class Checkout:
    def __init__(self, pricing: Pricing = no_discount) -> None:
        raise NotImplementedError("TODO")

    def total(self, prices: list[int]) -> int:
        raise NotImplementedError("TODO")


# --- Observer ----------------------------------------------------------------
class EventBus:
    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def subscribe(self, event: str, handler: Callable[[Any], None]) -> Callable[[], None]:
        raise NotImplementedError("TODO")

    def publish(self, event: str, payload: Any) -> int:
        raise NotImplementedError("TODO")


def main() -> None:
    Config.reset()
    c1 = Config()
    c1.settings["debug"] = True
    c2 = Config()
    print("singleton same object:", c1 is c2, "| settings survive:", c2.settings)

    shapes = [make_shape(s) for s in ({"kind": "circle", "r": 1},
                                      {"kind": "square", "side": 3},
                                      {"kind": "rect", "w": 2, "h": 5})]
    print("areas:", [round(s.area(), 4) for s in shapes])
    try:
        make_shape({"kind": "hexagon"})
    except ValueError as exc:
        print("ValueError:", exc)
    try:
        make_shape_if_chain({"kind": "rect", "w": 2, "h": 5})
    except ValueError as exc:
        print("if-chain forgot rect -> ValueError:", exc)

    cart = [1000, 500, 300, 200]
    co = Checkout()
    print("no discount:", co.total(cart))
    co.pricing = percent_off(10)
    print("10% off   :", co.total(cart))
    co.pricing = buy_n_get_one(2)
    print("3 for 2   :", co.total(cart),
          "| lambda strategy:", Checkout(lambda p: max(p)).total(cart))

    bus, seen = EventBus(), []
    unsub = bus.subscribe("order", lambda p: seen.append(f"email:{p}"))
    bus.subscribe("order", lambda p: seen.append(f"audit:{p}"))
    print("handlers run:", bus.publish("order", "A1"), "| no subscribers:", bus.publish("x", 0))
    unsub()
    bus.publish("order", "A2")
    print("seen:", seen)


if __name__ == "__main__":
    main()
