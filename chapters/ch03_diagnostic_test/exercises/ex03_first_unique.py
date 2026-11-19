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

Hints
-----
- collections.Counter counts in one pass.
- Scan the ORIGINAL list a second time, not the Counter, to respect arrival order.
- Wrap each test call in try/except and pass a copy of the input.

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
    raise NotImplementedError("TODO")


def first_unique(ids: Sequence[Hashable]) -> Hashable | None:
    raise NotImplementedError("TODO")


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
    raise NotImplementedError("TODO")


def main() -> None:
    for ids, _ in CASES[:4]:
        print(f"first_unique({ids}) = {first_unique(ids)!r}")
    print()
    for name, fn in [("first_unique", first_unique), ("brute_force", brute_force),
                     ("tempting_least_frequent", tempting_least_frequent)]:
        print(f"score {name:<24} {score_submission(fn)}/4")


if __name__ == "__main__":
    main()
