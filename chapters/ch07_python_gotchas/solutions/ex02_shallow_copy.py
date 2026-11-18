"""
Exercise 02 — Shallow Copy of a Nested Config           [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (references) · Target time: 8 min

Problem
-------
`with_override(config, section, key, value)` must return a NEW nested config
(a dict of dicts) in which `config[section][key] == value`, while leaving the
caller's `config` completely untouched. The buggy version uses `dict.copy()`,
which copies only the outer dict: the inner dicts are still shared, so the
override leaks into the original.

Examples
--------
>>> base = {"db": {"host": "localhost", "port": 5432}}
>>> new = solve(base, "db", "port", 6543)
>>> base["db"]["port"], new["db"]["port"]
(5432, 6543)

Constraints
-----------
- `section` may or may not already exist in `config`.
- Values inside sections may themselves be lists or dicts.

Approach ladder
---------------
1. Buggy  — `new = config.copy()` → shallow; `new[section]` IS `config[section]`.
2. Fixed  — `copy.deepcopy(config)` then assign. O(size of config) time/space.
3. Leaner — copy only the path you change:
   `{**config, section: {**config.get(section, {}), key: value}}`. Cheaper, but
   any *other* nested values are still shared (fine if nobody mutates them).

Follow-ups
----------
- Name three ways to make a shallow copy of a list (`a[:]`, `list(a)`, `a.copy()`).
- When does `deepcopy` surprise you? (Custom objects, cycles, large data — it is slow.)
"""
from __future__ import annotations

import copy
from typing import Any

Config = dict[str, dict[str, Any]]


def buggy_with_override(config: Config, section: str, key: str, value: Any) -> Config:
    new = config.copy()                      # shallow: inner dicts are shared
    new.setdefault(section, {})[key] = value
    return new


def solve(config: Config, section: str, key: str, value: Any) -> Config:
    """Return a deep copy of `config` with config[section][key] = value."""
    new = copy.deepcopy(config)
    new.setdefault(section, {})[key] = value
    return new


def main() -> None:
    base = {"db": {"host": "localhost", "port": 5432}, "tags": {"env": ["dev"]}}
    buggy = buggy_with_override(base, "db", "port", 6543)
    print("buggy: new port", buggy["db"]["port"], "| original port", base["db"]["port"])

    base = {"db": {"host": "localhost", "port": 5432}, "tags": {"env": ["dev"]}}
    fixed = solve(base, "db", "port", 6543)
    print("fixed: new port", fixed["db"]["port"], "| original port", base["db"]["port"])
    fixed["tags"]["env"].append("prod")
    print("fixed: nested list shared?", fixed["tags"]["env"] is base["tags"]["env"])
    print("new section:", solve(base, "cache", "ttl", 60)["cache"])


if __name__ == "__main__":
    main()
