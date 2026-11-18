"""
Exercise 06 — Equal Points That Cannot Go in a Set      [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (equality & hashing) · Target time: 8 min

Problem
-------
`Point` defines `__eq__` so that two points with the same coordinates compare
equal. `count_unique(points)` must return how many distinct points a list holds.
The buggy `Point` defines `__eq__` but not `__hash__`; Python then sets
`__hash__ = None`, so points are unhashable and `set(points)` raises TypeError.

Examples
--------
>>> count_unique([Point(1, 2), Point(1, 2), Point(3, 4)])
2
>>> Point(1, 2) in {Point(1, 2)}
True

Constraints
-----------
- Points are treated as immutable values once created.

Approach ladder
---------------
1. Buggy  — `__eq__` only → `Point.__hash__ is None` → unhashable.
2. Fixed  — add `__hash__` that hashes the SAME fields `__eq__` compares:
   `hash((self.x, self.y))`. Equal objects must have equal hashes.
3. Idiomatic — `@dataclass(frozen=True)` generates `__eq__` and `__hash__` together
   and blocks mutation (mutating a key after insertion would "lose" it in the set).

Follow-ups
----------
- Why must equal objects hash equal, but not vice versa? (Dict lookup checks hash
  first, then `==`; collisions are allowed, mismatched hashes are not.)
- What goes wrong if you hash a MUTABLE field and then mutate it?
"""
from __future__ import annotations

from dataclasses import dataclass


class BuggyPoint:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuggyPoint):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)
    # no __hash__  ->  Python sets BuggyPoint.__hash__ = None


@dataclass(frozen=True)
class Point:
    x: int
    y: int


def buggy_count_unique(points: list[BuggyPoint]) -> int:
    return len(set(points))


def count_unique(points: list[Point]) -> int:
    """Number of distinct points (O(n) average with hashing)."""
    return len(set(points))


def main() -> None:
    print("BuggyPoint.__hash__ is None:", BuggyPoint.__hash__ is None)
    try:
        buggy_count_unique([BuggyPoint(1, 2), BuggyPoint(1, 2)])
    except TypeError as exc:
        print("buggy:", type(exc).__name__, "-", exc)
    pts = [Point(1, 2), Point(1, 2), Point(3, 4)]
    print("fixed unique:", count_unique(pts))
    print("fixed equal hashes:", hash(Point(1, 2)) == hash(Point(1, 2)))
    print("fixed membership:", Point(3, 4) in set(pts))


if __name__ == "__main__":
    main()
