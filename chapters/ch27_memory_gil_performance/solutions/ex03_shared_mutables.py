"""
Exercise 03 — Find Hidden Aliasing in a Nested Structure   [Tier: ◆ Extended]
Chapter 27 · Pattern: identity-aware graph walk · Target time: 25 min

Problem
-------
Containers hold references, not values. `[[0] * 3] * 3` is three references
to ONE inner list, and a shallow copy shares every inner object with the
original. Write two helpers that make this visible.

1. `aliases(root)` walks lists, tuples, dicts (values) and sets reachable from
   `root` and returns a list of (first_path, alias_path) pairs: every time a
   MUTABLE object (list, dict, set, bytearray) is reached a second time, pair
   the new path with the path where it was first seen. Paths look like
   "root[1]['k'][0]". Tuples and other immutables may repeat freely.
2. `shared_between(a, b)` returns the sorted paths in `b` whose mutable object
   is also reachable from `a` (so mutating one structure changes the other).

Visit order: list/tuple by index, dict by insertion order, set elements are
never mutable (they must be hashable), so sets need no descent.

Examples
--------
>>> aliases([[0] * 3] * 3)
[('root[0]', 'root[1]'), ('root[0]', 'root[2]')]
>>> grid = [[0], [1]]; shared_between(grid, list(grid))
['root[0]', 'root[1]']

Constraints
-----------
- Structures may contain cycles (a list that contains itself): report the
  alias, never recurse forever.

Approach ladder
---------------
1. Brute force — compare every pair of sub-objects with `is`: O(m^2) for m
   reachable objects.
2. Improved   — `==` instead of `is`. Wrong: equal-but-separate lists are not
   aliases; aliasing is an identity question.
3. Optimal    — one DFS with a dict {id(obj): first_path}; a repeat id is an
   alias and is not descended into again (this also stops cycles). O(m)
   time and space. Keep the objects alive while walking so ids cannot be
   reused (they are, because `root` holds them).

Hints
-----
- `id()` is only unique among objects alive at the same time.
- Use `isinstance(x, (list, dict, set, bytearray))` for "mutable".

Follow-ups
----------
- Which `copy` call makes `shared_between(a, copy)` empty? (`copy.deepcopy`;
  shallow vs deep copy is taught in → §7.2.)
- Why can a tuple still change "value"? (`t = ([],)`; `t[0].append(1)`: the
  tuple's references are fixed, the list they point to is not.)
"""
from __future__ import annotations

import copy

MUTABLE = (list, dict, set, bytearray)


def _walk(root: object, visit) -> None:
    """DFS calling visit(obj, path) for every container slot; visit returns
    True when the object should be descended into."""
    stack = [(root, "root")]
    while stack:
        obj, path = stack.pop()
        if not visit(obj, path):
            continue
        if isinstance(obj, (list, tuple)):
            children = [(v, f"{path}[{i}]") for i, v in enumerate(obj)]
        elif isinstance(obj, dict):
            children = [(v, f"{path}[{k!r}]") for k, v in obj.items()]
        else:
            continue
        stack.extend(reversed(children))           # pop in natural order


def aliases(root: object) -> list[tuple[str, str]]:
    first_seen: dict[int, str] = {}
    found: list[tuple[str, str]] = []

    def visit(obj: object, path: str) -> bool:
        if not isinstance(obj, MUTABLE):
            return True                             # tuples: descend, never an alias
        key = id(obj)
        if key in first_seen:
            found.append((first_seen[key], path))
            return False                            # already explored (also stops cycles)
        first_seen[key] = path
        return True

    _walk(root, visit)
    return found


def shared_between(a: object, b: object) -> list[str]:
    in_a: set[int] = set()

    def collect(obj: object, path: str) -> bool:
        if isinstance(obj, MUTABLE):
            if id(obj) in in_a:
                return False
            in_a.add(id(obj))
        return True

    _walk(a, collect)
    hits: list[str] = []
    seen_b: set[int] = set()

    def check(obj: object, path: str) -> bool:
        if isinstance(obj, MUTABLE):
            if id(obj) in in_a:
                hits.append(path)
                return False                        # everything below is shared too
            if id(obj) in seen_b:
                return False
            seen_b.add(id(obj))
        return True

    _walk(b, check)
    return sorted(hits)


def main() -> None:
    grid = [[0] * 3] * 3
    print("[[0]*3]*3 aliases:", aliases(grid))
    print("comprehension grid aliases:", aliases([[0] * 3 for _ in range(3)]))
    loop: list = [1]
    loop.append(loop)
    print("self-containing list:", aliases(loop))
    cfg = {"a": [1], "b": ([2], [3])}
    print("shallow copy shares:", shared_between(cfg, copy.copy(cfg)))
    print("deep copy shares:", shared_between(cfg, copy.deepcopy(cfg)))
    t = ([],)
    t[0].append(1)
    print("tuple holding a mutated list:", t)
    print("tuple contents aliased:", aliases((t[0], t[0])))


if __name__ == "__main__":
    main()
