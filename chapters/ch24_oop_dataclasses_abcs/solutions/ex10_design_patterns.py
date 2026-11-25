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

Approach ladder
---------------
1. Brute force — one `if kind == ...` chain per decision point and hard-wired calls
   between objects: O(1) dispatch, but every new kind or listener edits existing code.
2. Optimal    — the pattern with Python idioms: a module-level object or `__new__` for a
   singleton, a dict registry for factories (O(1) lookup), plain functions/closures as
   strategies, a dict of handler lists for observers. Each adds behaviour without
   editing the caller (open/closed principle).

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
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialised:                       # __init__ runs on every Config()
            return
        self.settings: dict[str, Any] = {"debug": False}
        self._initialised = True

    @classmethod
    def reset(cls) -> None:
        cls._instance = None


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
        self.r = r

    def area(self) -> float:
        return math.pi * self.r ** 2


@register("square")
class Square:
    def __init__(self, side: float) -> None:
        self.side = side

    def area(self) -> float:
        return self.side ** 2


@register("rect")
class Rect:
    def __init__(self, w: float, h: float) -> None:
        self.w, self.h = w, h

    def area(self) -> float:
        return self.w * self.h


def make_shape(spec: dict[str, Any]) -> Any:
    params = dict(spec)
    kind = params.pop("kind")
    try:
        cls = SHAPES[kind]
    except KeyError:
        raise ValueError(f"unknown kind {kind!r}; known: {sorted(SHAPES)}") from None
    return cls(**params)


def make_shape_if_chain(spec: dict[str, Any]) -> Any:
    """Rung 1: every new shape edits this function."""
    if spec["kind"] == "circle":
        return Circle(spec["r"])
    if spec["kind"] == "square":
        return Square(spec["side"])
    raise ValueError(spec["kind"])


# --- Strategy ----------------------------------------------------------------
Pricing = Callable[[list[int]], int]


def no_discount(prices: list[int]) -> int:
    return sum(prices)


def percent_off(p: int) -> Pricing:
    def pricing(prices: list[int]) -> int:
        return (sum(prices) * (100 - p) + 50) // 100   # round half up, whole cents
    return pricing


def buy_n_get_one(n: int) -> Pricing:
    def pricing(prices: list[int]) -> int:
        ordered = sorted(prices)                      # cheapest items are the free ones
        free = len(prices) // (n + 1)
        return sum(ordered[free:])
    return pricing


class Checkout:
    def __init__(self, pricing: Pricing = no_discount) -> None:
        self.pricing = pricing                        # swappable at runtime

    def total(self, prices: list[int]) -> int:
        return self.pricing(prices)


# --- Observer ----------------------------------------------------------------
class EventBus:
    def __init__(self) -> None:
        self._handlers: defaultdict[str, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable[[Any], None]) -> Callable[[], None]:
        self._handlers[event].append(handler)
        return lambda: self._handlers[event].remove(handler)

    def publish(self, event: str, payload: Any) -> int:
        handlers = list(self._handlers.get(event, ()))  # copy: handlers may unsubscribe
        for h in handlers:
            h(payload)
        return len(handlers)


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
