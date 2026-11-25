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
    raise NotImplementedError("TODO")


def shared_between(a: object, b: object) -> list[str]:
    raise NotImplementedError("TODO")


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
