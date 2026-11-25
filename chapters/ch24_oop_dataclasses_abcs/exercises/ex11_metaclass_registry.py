"""
Exercise 11 — Plugin Registry: Metaclass vs __init_subclass__  [Tier: ○ Reference]
Chapter 24 · Pattern: class-creation hooks · Target time: 20 min

Problem
-------
Every plugin class must declare a non-empty string class attribute `name`, and every
plugin must be findable by that name without a hand-maintained list.

1. `PluginMeta(type)` — a metaclass whose `__new__` builds the class, then (for every
   class except the root `MetaPlugin`) checks `name` and records the class in
   `PluginMeta.registry`. A missing/empty `name` or a duplicate name raises `TypeError`
   at CLASS-DEFINITION time.
2. `HookPlugin` — the same behaviour with `__init_subclass__` (no metaclass), recording
   subclasses in `HookPlugin.registry`.
3. `make_plugin_class(base, name, run)` — build a subclass of `base` dynamically with the
   3-argument `type(...)` call (or the metaclass, for MetaPlugin) whose `run(self, x)`
   returns `run(x)`.
4. `run_all(registry, x)` -> `{name: plugin().run(x)}` in sorted name order.

Examples
--------
>>> P = make_plugin_class(HookPlugin, "double", lambda x: 2 * x); run_all(HookPlugin.registry, 5)
{'double': 10}

Constraints
-----------
- Registration O(1) per class; run_all O(p log p) for p plugins.

Hints
-----
- `type(name, bases, namespace)` creates a class; a metaclass is just a subclass of
  `type` whose `__new__(mcls, name, bases, ns)` you override.
- Skip the root class: in the metaclass, `if bases:`; in `__init_subclass__` the root
  never triggers the hook (only subclasses do).
- `type(cls)` of a class built by `PluginMeta` is `PluginMeta`.

Follow-ups
----------
- Why do two unrelated metaclasses on two bases raise "metaclass conflict"?
- What does `__call__` on a metaclass control? (instance creation: `Cls(...)` calls
  `type(Cls).__call__`, which runs `__new__` then `__init__`.)
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any


DECORATED: dict[str, type] = {}


def register_plugin(cls: type) -> type:
    """Rung 2: opt-in class decorator; a class without it is silently missing."""
    raise NotImplementedError("TODO")


class PluginMeta(type):
    registry: dict[str, type] = {}

    def __new__(mcls, name: str, bases: tuple[type, ...], ns: dict[str, Any]) -> type:
        cls = super().__new__(mcls, name, bases, ns)
        # TODO: for non-root classes (bases non-empty) validate ns["name"] and register cls
        return cls


class MetaPlugin(metaclass=PluginMeta):
    name = ""

    def run(self, x: Any) -> Any:
        raise NotImplementedError("TODO")


class HookPlugin:
    registry: dict[str, type] = {}
    name = ""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        raise NotImplementedError("TODO")

    def run(self, x: Any) -> Any:
        raise NotImplementedError("TODO")


def make_plugin_class(base: type, name: str, run: Callable[[Any], Any]) -> type:
    raise NotImplementedError("TODO")


def run_all(registry: dict[str, type], x: Any) -> dict[str, Any]:
    raise NotImplementedError("TODO")


def main() -> None:
    class Upper(MetaPlugin):
        name = "upper"

        def run(self, x: str) -> str:
            return x.upper()

    class Reverse(HookPlugin):
        name = "reverse"

        def run(self, x: str) -> str:
            return x[::-1]

    @register_plugin
    class Plain:
        name = "plain"

    class Forgotten:
        name = "forgotten"

    print("decorator registry:", sorted(DECORATED), "<- Forgotten is missing")
    make_plugin_class(MetaPlugin, "shout", lambda s: s + "!")
    Dyn = make_plugin_class(HookPlugin, "length", len)
    print("meta registry:", sorted(PluginMeta.registry), "| type(Upper):", type(Upper).__name__)
    print("hook registry:", sorted(HookPlugin.registry), "| type(Reverse):", type(Reverse).__name__)
    print("dynamic class:", Dyn.__name__, Dyn.__mro__[1].__name__)
    print("run meta:", run_all(PluginMeta.registry, "abc"))
    print("run hook:", run_all(HookPlugin.registry, "abc"))
    for base in (MetaPlugin, HookPlugin):
        try:
            type(base)("Nameless", (base,), {})
        except TypeError as exc:
            print("TypeError:", exc)
    try:
        class Upper2(MetaPlugin):
            name = "upper"
    except TypeError as exc:
        print("TypeError:", exc)


if __name__ == "__main__":
    main()
