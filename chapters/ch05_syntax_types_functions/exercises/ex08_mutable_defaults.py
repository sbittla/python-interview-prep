"""
Exercise 08 — Fix the Mutable Default Argument                [Tier: ★ Core]
Chapter 05 · Pattern: default values are evaluated once · Target time: 10 min

Problem
-------
``buggy_register(name, registry=[])`` appends ``name`` to ``registry`` and returns it. Called
twice without a registry, the second call returns both names, because the default list is
created once, when ``def`` runs, and then shared by every call.

Write ``solve(name, registry=None)`` with the same contract but no shared state: each call
that omits ``registry`` gets a brand-new list. When a registry *is* passed, append to it and
return that same object (callers rely on the mutation). Also write
``tag_counts(words, counts=None)`` that returns a dict of word -> count, adding to ``counts``
when one is given.

Examples
--------
>>> solve("ada")
['ada']
>>> solve("grace")
['grace']
>>> shared = ["x"]; solve("y", shared) is shared
True

Constraints
-----------
- names are strings; registries are lists

Hints
-----
1. Run ``buggy_register`` twice and print ``buggy_register.__defaults__``. When was that list
   created?
2. Pick a default value that cannot be mutated and build the real container inside the body.
3. Your test for "no registry was passed" must not treat a caller's *empty* list as missing.

Follow-ups
----------
- When is a shared default useful on purpose?
- Where can you see the shared object?
"""
from __future__ import annotations


def buggy_register(name: str, registry: list[str] = []) -> list[str]:  # noqa: B006 (on purpose)
    registry.append(name)
    return registry


brute_force = buggy_register


def solve(name: str, registry: list[str] | None = None) -> list[str]:
    raise NotImplementedError("TODO")


def tag_counts(words: list[str], counts: dict[str, int] | None = None) -> dict[str, int]:
    raise NotImplementedError("TODO")


def main() -> None:
    print("buggy 1:", buggy_register("ada"))
    print("buggy 2:", buggy_register("grace"), "<- leaked from call 1")
    print("hidden default now:", buggy_register.__defaults__)
    print("fixed 1:", solve("ada"))
    print("fixed 2:", solve("grace"))
    empty: list[str] = []
    print("caller's empty list is mutated:", solve("linus", empty) is empty, empty)
    print("tag_counts:", tag_counts(["a", "b", "a"]), tag_counts(["c"]))


if __name__ == "__main__":
    main()
