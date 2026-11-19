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

Approach ladder
---------------
1. Brute force — repeatedly scan all pairs, fuse any two that overlap, restart until no pair
   fuses: O(n^3) worst case. Correct but each fusion triggers a full rescan.
2. Optimal    — sort by start (O(n log n)); then every interval either extends the last
   merged one (``start <= last_end``) or starts a new one. One sweep, O(n) after the sort,
   O(n) output space. Sorting is what makes "only compare with the last" valid.

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
    items = [list(iv) for iv in intervals]
    changed = True
    while changed:
        changed = False
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if a[0] <= b[1] and b[0] <= a[1]:          # overlap or touch
                    items[i] = [min(a[0], b[0]), max(a[1], b[1])]
                    del items[j]
                    changed = True
                    break
            if changed:
                break
    return sorted(items)


def merge(intervals: list[list[int]]) -> list[list[int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])                  # new list: input never aliased
    return merged


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
    passed = 0
    for intervals, expected in CASES:
        try:
            if fn(copy.deepcopy(intervals)) == expected:
                passed += 1
        except Exception:
            pass
    return 4 * passed // len(CASES)


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
