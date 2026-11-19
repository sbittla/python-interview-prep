"""
Exercise 04 — Diagnostic Q30: Merge Booked Intervals               [Tier: ★ Core]
Chapter 03 · Pattern: sort + linear sweep · Target time: 15 min

Problem
-------
A meeting room's bookings are closed intervals ``[start, end]`` (integers, start <= end) in no
particular order. Return the merged busy periods, sorted by start, where intervals that
overlap OR touch (``[1, 3]`` and ``[3, 5]``) become one. Do not mutate the input.

Also write ``score_submission(fn)`` exactly as in ex03: ``4 * passed // len(CASES)``.

Examples
--------
>>> merge([[8, 10], [1, 3], [2, 6]])
[[1, 6], [8, 10]]
>>> merge([[1, 3], [3, 5]])
[[1, 5]]

Constraints
-----------
- 0 <= len(intervals) <= 10^5; -10^9 <= start <= end <= 10^9.

Hints
-----
- After sorting by start, only the last merged interval can overlap the next one.
- Touching counts as overlapping: compare with <=.
- Extend with max(), not assignment: think of [[1, 10], [2, 3]].
- Append new lists ([start, end]) so the caller's lists are never modified.

Wrong-but-tempting
------------------
- ``last[1] = end`` instead of ``max(last[1], end)``: breaks on nesting, ``[[1, 10], [2, 3]]``.
- Forgetting to sort: ``[[5, 6], [1, 5]]`` is not merged.
- ``start < last_end`` instead of ``<=``: touching intervals stay separate.
- Appending the caller's inner lists and then editing them: mutates the input.

Follow-ups
----------
- Insert one new interval into an already merged list in O(n) (→ Chapter 17).
- Minimum number of rooms for all bookings (heap or sweep line, → Chapters 15 and 17).
"""
from __future__ import annotations

import copy
from collections.abc import Callable


def brute_force(intervals: list[list[int]]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def merge(intervals: list[list[int]]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def tempting_no_max(intervals: list[list[int]]) -> list[list[int]]:
    """WRONG on purpose: overwrites the end instead of taking the max."""
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = end
        else:
            merged.append([start, end])
    return merged


CASES = [
    ([[8, 10], [1, 3], [2, 6]], [[1, 6], [8, 10]]),
    ([], []),
    ([[4, 4]], [[4, 4]]),
    ([[1, 3], [3, 5]], [[1, 5]]),                    # touching
    ([[1, 10], [2, 3], [4, 5]], [[1, 10]]),          # nested
    ([[5, 6], [1, 2]], [[1, 2], [5, 6]]),            # disjoint, unsorted
    ([[-5, -1], [-2, 0], [2, 2]], [[-5, 0], [2, 2]]),
    ([[1, 4], [0, 0], [0, 2]], [[0, 4]]),
]


def score_submission(fn: Callable) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    for intervals, _ in CASES[:5]:
        print(f"merge({intervals}) = {merge(intervals)}")
    original = [[2, 6], [1, 3]]
    merge(original)
    print(f"input after merge: {original}  (unchanged)")
    print()
    for name, fn in [("merge", merge), ("brute_force", brute_force),
                     ("tempting_no_max", tempting_no_max)]:
        print(f"score {name:<16} {score_submission(fn)}/4")


if __name__ == "__main__":
    main()
