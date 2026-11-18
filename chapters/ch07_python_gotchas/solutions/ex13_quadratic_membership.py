"""
Exercise 13 — Deduplication That Gets Slow              [Tier: ★ Core]
Chapter 07 · Pattern: find-and-fix (performance) · Target time: 8 min

Problem
-------
`dedupe(items)` returns the items with duplicates removed, keeping the FIRST
occurrence order. The buggy version is correct but keeps `seen` in a LIST, so
`x not in seen` scans the list: O(n) per check, O(n^2) overall. With 10^5 items
that is ~5 * 10^9 comparisons — a time-limit-exceeded verdict.

The demo counts how many `==` comparisons each version performs (deterministic,
unlike timings) using a small wrapper class.

Examples
--------
>>> dedupe([3, 1, 3, 2, 1])
[3, 1, 2]

Constraints
-----------
- 0 <= len(items) <= 10**5; items are hashable.

Approach ladder
---------------
1. Buggy  — list membership: O(n^2) time.
2. Fixed  — set membership: O(n) average time, O(n) space.
3. One-liner — `list(dict.fromkeys(items))` (dicts keep insertion order, 3.7+).

Follow-ups
----------
- Items unhashable (lists)? Convert to tuples, or fall back to O(n^2) / sorting.
- Worst case of set lookup? O(n) under adversarial hash collisions — average O(1).
"""
from __future__ import annotations

from typing import Hashable, TypeVar

T = TypeVar("T", bound=Hashable)


class Counted:
    """Wraps a value and counts every == comparison performed on any instance."""
    comparisons = 0

    def __init__(self, value: int) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        Counted.comparisons += 1
        return isinstance(other, Counted) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


def buggy_dedupe(items: list[T]) -> list[T]:
    seen: list[T] = []
    out: list[T] = []
    for x in items:
        if x not in seen:          # O(len(seen)) scan
            seen.append(x)
            out.append(x)
    return out


def dedupe(items: list[T]) -> list[T]:
    """Order-preserving dedupe with a set: O(n) average."""
    seen: set[T] = set()
    out: list[T] = []
    for x in items:
        if x not in seen:          # O(1) average hash lookup
            seen.add(x)
            out.append(x)
    return out


def comparisons_used(func, n: int) -> int:
    Counted.comparisons = 0
    func([Counted(i) for i in range(n)])
    return Counted.comparisons


def main() -> None:
    print("buggy:", buggy_dedupe([3, 1, 3, 2, 1]))
    print("fixed:", dedupe([3, 1, 3, 2, 1]))
    print("dict.fromkeys:", list(dict.fromkeys([3, 1, 3, 2, 1])))
    print(f"{'n':>6} {'list ==':>10} {'set ==':>8}")
    for n in (100, 200, 400, 800):
        print(f"{n:>6} {comparisons_used(buggy_dedupe, n):>10} {comparisons_used(dedupe, n):>8}")


if __name__ == "__main__":
    main()
