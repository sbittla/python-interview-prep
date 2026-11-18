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

Approach ladder
---------------
1. Brute force (the bug) — ``registry=[]``. Looks right in a single call, fails across calls.
2. Optimal    — use ``None`` as a sentinel and create the list inside the body:
   ``if registry is None: registry = []``. O(1) extra work per call. Test with ``is None``,
   not truthiness: ``registry or []`` would wrongly replace a caller's *empty* list.

Follow-ups
----------
- When is a shared default useful on purpose? A deliberate cache, but say so (or use
  ``functools.lru_cache``).
- Where can you see the shared object? ``buggy_register.__defaults__``.
"""
from __future__ import annotations


def buggy_register(name: str, registry: list[str] = []) -> list[str]:  # noqa: B006 (on purpose)
    registry.append(name)
    return registry


brute_force = buggy_register


def solve(name: str, registry: list[str] | None = None) -> list[str]:
    if registry is None:
        registry = []
    registry.append(name)
    return registry


def tag_counts(words: list[str], counts: dict[str, int] | None = None) -> dict[str, int]:
    if counts is None:
        counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return counts


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
