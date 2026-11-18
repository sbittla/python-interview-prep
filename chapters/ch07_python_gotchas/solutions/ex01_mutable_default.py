"""
Exercise 01 — Mutable Default Argument                  [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (references) · Target time: 5 min

Problem
-------
`add_tag(tag, tags)` should append `tag` to the list `tags` and return it. When
the caller omits `tags`, a *fresh* empty list must be used for that call. The
buggy version uses `tags=[]` as the default, so every call that omits `tags`
shares (and grows) the same list.

Examples
--------
>>> solve("python")
['python']
>>> solve("sql")          # a new call starts from an empty list again
['sql']
>>> solve("x", ["a"])
['a', 'x']

Constraints
-----------
- `tags`, when given, is a list that the caller expects to be modified and returned.

Approach ladder
---------------
1. Buggy  — `def add_tag(tag, tags=[])`: the default list is created ONCE, when
   the `def` statement runs, and stored in `add_tag.__defaults__`.
2. Fixed  — use the sentinel `None` and create the list inside the body:
   `if tags is None: tags = []`. O(1) per call.
3. Variant — if `None` is a legitimate value, use a private sentinel object
   (`_MISSING = object()`).

Follow-ups
----------
- Where can you see the shared default? (`add_tag.__defaults__`)
- Is a tuple default (`tags=()`) safe? (Yes — tuples are immutable.)
- When is the shared default deliberately useful? (A crude memo cache — but
  prefer `functools.lru_cache`.)
"""
from __future__ import annotations


def buggy_add_tag(tag: str, tags: list[str] = []) -> list[str]:  # noqa: B006 (the bug)
    tags.append(tag)
    return tags


def solve(tag: str, tags: list[str] | None = None) -> list[str]:
    """Append `tag` to `tags` (or to a brand-new list) and return the list."""
    if tags is None:
        tags = []
    tags.append(tag)
    return tags


def main() -> None:
    print("buggy call 1:", buggy_add_tag("python"))
    print("buggy call 2:", buggy_add_tag("sql"))
    print("buggy defaults now:", buggy_add_tag.__defaults__)
    print("fixed call 1:", solve("python"))
    print("fixed call 2:", solve("sql"))
    print("fixed defaults:", solve.__defaults__)
    print("explicit list:", solve("x", ["a"]))


if __name__ == "__main__":
    main()
