"""
Exercise 08 — Class Decorators and Decorator Classes                 [Tier: ◆ Extended]
Chapter 25 · Pattern: decorate a class / a class that decorates · Target time: 25 min

Problem
-------
1. `register(registry, name=None)` — a decorator factory that stores the
   decorated class (or function) in `registry` under `name` or its `__name__`,
   raises KeyError on a duplicate name, and returns the object UNCHANGED.
2. `auto_repr(cls)` — a class decorator that adds a `__repr__` built from the
   parameters of `cls.__init__` (excluding self), e.g. `Point(x=1, y=2)`, and
   returns the same class.
3. `CountCalls` — a decorator written as a class: `CountCalls(func)` is callable,
   counts `.calls`, and keeps func's metadata. It must ALSO work on methods: a
   plain class with `__call__` is not a descriptor, so `obj.method()` would not
   receive `self`. Implement `__get__` to bind the instance.

Examples
--------
>>> PLUGINS = {}
>>> Csv = register(PLUGINS)(type("Csv", (), {}))
>>> sorted(PLUGINS), PLUGINS["Csv"] is Csv
(['Csv'], True)

Constraints
-----------
- Class decorators run once, when the class statement finishes executing.

Approach ladder
---------------
1. Brute force — hand-write __repr__ in every class, and a central list of
   plugins that must be edited for each new class (easy to forget).
2. Class decorator — `cls = auto_repr(cls)` after the class body: adds behaviour
   without inheritance or a metaclass, O(p) to build each repr for p params.
3. Decorator class — use when the decorator needs rich state or methods;
   requires `functools.update_wrapper(self, func)` and `__get__` (returning
   `types.MethodType(self, obj)`) to behave like a function on methods.
   Why: a function wrapper is a descriptor automatically; a class instance is not.

Hints
-----
- `inspect.signature(cls.__init__).parameters` lists the init parameters.
- Decorators are applied bottom-up; @dataclass is itself a class decorator (Ch. 24).
- `types.MethodType(callable, instance)` creates a bound method.

Follow-ups
----------
- Singleton as a class decorator: why does `isinstance(x, Cls)` break if the
  decorator returns a function? (§24.11 shows a safer version.)
- Wrap every method of a class with log_calls (iterate over vars(cls)).
- When would you choose a metaclass or __init_subclass__ instead (§24.12)?
"""
from __future__ import annotations

import inspect
import types
from functools import update_wrapper


def register(registry: dict, name: str | None = None):
    def decorator(obj):
        key = name or obj.__name__
        if key in registry:
            raise KeyError(f"duplicate registration: {key!r}")
        registry[key] = obj
        return obj                                  # unchanged
    return decorator


def auto_repr(cls: type) -> type:
    params = [p for p in inspect.signature(cls.__init__).parameters if p != "self"]

    def __repr__(self) -> str:
        fields = ", ".join(f"{p}={getattr(self, p)!r}" for p in params)
        return f"{type(self).__name__}({fields})"

    cls.__repr__ = __repr__
    return cls


class CountCalls:
    def __init__(self, func) -> None:
        update_wrapper(self, func)                  # copies __name__, __doc__, ...
        self.func, self.calls = func, 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype=None):
        if obj is None:                             # accessed on the class
            return self
        return types.MethodType(self, obj)          # bind like a function


class CountCallsNoGet:
    """Same as CountCalls but without __get__: breaks on methods."""

    def __init__(self, func) -> None:
        update_wrapper(self, func)
        self.func, self.calls = func, 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)


def main() -> None:
    exporters: dict[str, type] = {}

    @register(exporters)
    @auto_repr
    class Csv:
        def __init__(self, sep: str = ",") -> None:
            self.sep = sep

    @register(exporters, name="json")
    @auto_repr
    class JsonExporter:
        def __init__(self, indent: int, sort_keys: bool = False) -> None:
            self.indent, self.sort_keys = indent, sort_keys

    print("registry:", sorted(exporters))
    print("reprs:", Csv(), exporters["json"](2))
    try:
        register(exporters)(Csv)
    except KeyError as exc:
        print("duplicate:", exc)

    class Cart:
        def __init__(self) -> None:
            self.items: list[str] = []

        @CountCalls
        def add(self, item: str) -> int:
            """Add an item; return the new size."""
            self.items.append(item)
            return len(self.items)

        @CountCallsNoGet
        def add_broken(self, item: str) -> int:
            self.items.append(item)
            return len(self.items)

    cart = Cart()
    print("add:", cart.add("tea"), cart.add("milk"), "| calls =", Cart.add.calls,
          "| name =", Cart.add.__name__, "| doc =", Cart.add.__doc__)
    try:
        cart.add_broken("jam")
    except TypeError as exc:
        print("without __get__:", exc)


if __name__ == "__main__":
    main()
