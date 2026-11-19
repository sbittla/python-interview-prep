"""
Exercise 03 — Diagnostic Q29: First Unique Value                   [Tier: ★ Core]
Chapter 03 · Pattern: frequency count with a hash map · Target time: 15 min

Problem
-------
A login log is a list of user ids in arrival order. Return the first id that occurs exactly
once in the whole list, or ``None`` if every id repeats (or the list is empty).

Also write ``score_submission(fn)``: run ``fn`` on the hidden cases in ``CASES`` and return the
diagnostic points, ``4 * passed // len(CASES)`` (0-4). A case whose call raises counts as
failed; ``fn`` must not be able to corrupt a later case by mutating its input.

Examples
--------
>>> first_unique(["ann", "bob", "ann", "cy", "bob"])
'cy'
>>> first_unique(["a", "a"]) is None
True

Constraints
-----------
- 0 <= len(ids) <= 10^5; ids are hashable (strings or ints); do not mutate the input.

Approach ladder
---------------
1. Brute force — for each id, ``ids.count(x) == 1``: O(n^2) time, O(1) extra space.
   Fine for 100 ids, ~10^10 steps for 10^5: this is why we move up a rung.
2. Optimal    — one pass to count (``Counter``), one pass in the original order to find the
   first count of 1: O(n) time, O(k) space for k distinct ids.

Wrong-but-tempting
------------------
- ``[x for x in set(ids) if ...][0]``: a set loses arrival order, so "first" becomes arbitrary.
- ``min(counts, key=counts.get)``: returns the *least frequent* id, which may occur twice
  (implemented below as ``tempting_least_frequent``; it scores 3/4).
- Returning ``ids[0]`` when nothing is unique instead of ``None``.

Follow-ups
----------
- Stream version: ids arrive one by one and you must answer after each (dict + ordered set).
- Return the first k unique ids.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Hashable, Sequence


def brute_force(ids: Sequence[Hashable]) -> Hashable | None:
    for x in ids:
        if ids.count(x) == 1:
            return x
    return None


def first_unique(ids: Sequence[Hashable]) -> Hashable | None:
    counts = Counter(ids)
    for x in ids:
        if counts[x] == 1:
            return x
    return None


def tempting_least_frequent(ids: Sequence[Hashable]) -> Hashable | None:
    """WRONG on purpose: least frequent id, even if it occurs more than once."""
    counts = Counter(ids)
    return min(counts, key=counts.get) if counts else None


CASES = [
    (["ann", "bob", "ann", "cy", "bob"], "cy"),
    ([], None),
    (["a", "a"], None),
    (["solo"], "solo"),
    ([3, 1, 3, 2, 1], 2),
    (["x", "y", "x", "y", "z", "w"], "z"),
    (["b", "a", "b", "a", "b"], None),   # all repeat, uneven counts
    ([0, 0, 0, 7], 7),                   # falsy id 0 must not confuse the check
]


def score_submission(fn: Callable) -> int:
    passed = 0
    for ids, expected in CASES:
        try:
            if fn(list(ids)) == expected:   # fresh copy: a mutating fn can't break later cases
                passed += 1
        except Exception:
            pass
    return 4 * passed // len(CASES)


def main() -> None:
    for ids, _ in CASES[:4]:
        print(f"first_unique({ids}) = {first_unique(ids)!r}")
    print()
    for name, fn in [("first_unique", first_unique), ("brute_force", brute_force),
                     ("tempting_least_frequent", tempting_least_frequent)]:
        print(f"score {name:<24} {score_submission(fn)}/4")


if __name__ == "__main__":
    main()
