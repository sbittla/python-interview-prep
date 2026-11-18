"""
Exercise 01 — Activity Selection / Non-overlapping Intervals        [Tier: ★ Core]
Chapter 20 · Pattern: greedy, sort by end time · Target time: 20 min

Problem
-------
You are given meetings as half-open intervals [start, end). Two meetings conflict when they
overlap; meetings that merely touch (one ends at 10, the next starts at 10) do not conflict.
1. `max_activities(intervals)` returns the largest number of meetings one person can attend.
2. `min_removals(intervals)` returns the fewest meetings to cancel so that none overlap.
3. `select(intervals)` returns one optimal set of chosen meetings, in the order chosen.

Examples
--------
>>> max_activities([(1, 4), (3, 5), (0, 6), (5, 7), (8, 9), (5, 9)])
3
>>> min_removals([(1, 2), (2, 3), (3, 4), (1, 3)])
1

Constraints
-----------
- 0 <= len(intervals) <= 10^5, start < end, integers.

Approach ladder
---------------
1. Brute force — try every subset, keep the largest conflict-free one. O(2^n * n) time.
2. Tempting greedy rules that FAIL — earliest start, shortest duration, fewest conflicts.
3. Optimal — sort by end time, take every interval that starts at or after the last chosen
   end. O(n log n) time, O(1) extra space beyond the sort. Exchange argument: the interval
   that finishes first can replace the first interval of any optimal answer, leaving at
   least as much room for the rest.

Hints
-----
- Which choice leaves the most room for everything that comes after it?
- min_removals = n - max_activities.

Follow-ups
----------
- Weighted intervals (each meeting has a value): greedy fails, use DP + binary search.
- Minimum meeting rooms (attend ALL meetings): sort starts/ends or use a min-heap of ends.
- Closed intervals where touching counts as overlap: change `>=` to `>`.
"""
from __future__ import annotations

from itertools import combinations


def _compatible(chosen: list[tuple[int, int]]) -> bool:
    ordered = sorted(chosen)
    return all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:]))


def brute_force(intervals: list[tuple[int, int]]) -> int:
    """Largest compatible subset by trying sizes from n downwards. Exponential."""
    for k in range(len(intervals), 0, -1):
        if any(_compatible(list(c)) for c in combinations(intervals, k)):
            return k
    return 0


def greedy_by(intervals: list[tuple[int, int]], key) -> int:
    """Generic 'sort by key, take if compatible with everything taken' greedy."""
    chosen: list[tuple[int, int]] = []
    for iv in sorted(intervals, key=key):
        if all(iv[1] <= c[0] or c[1] <= iv[0] for c in chosen):
            chosen.append(iv)
    return len(chosen)


def select(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Earliest-finish-first greedy; returns the chosen intervals."""
    chosen: list[tuple[int, int]] = []
    last_end = float("-inf")
    for start, end in sorted(intervals, key=lambda iv: iv[1]):
        if start >= last_end:          # touching is fine for half-open intervals
            chosen.append((start, end))
            last_end = end
    return chosen


def max_activities(intervals: list[tuple[int, int]]) -> int:
    return len(select(intervals))


def min_removals(intervals: list[tuple[int, int]]) -> int:
    return len(intervals) - max_activities(intervals)


def main() -> None:
    meetings = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]
    print("meetings      :", meetings)
    print("chosen        :", select(meetings))
    print("max_activities:", max_activities(meetings), "| brute force:", brute_force(meetings))
    print("min_removals  :", min_removals(meetings))
    print()
    # Counterexamples for tempting greedy rules
    cases = {
        "earliest start": [(0, 10), (1, 2), (3, 4)],
        "shortest first": [(0, 5), (4, 7), (6, 11)],
        "fewest conflicts": [(0, 2), (2, 4), (4, 6), (6, 8), (1, 3), (1, 3), (1, 3),
                             (3, 5), (5, 7), (5, 7), (5, 7)],
    }
    rules = {
        "earliest start": lambda iv: iv[0],
        "shortest first": lambda iv: iv[1] - iv[0],
        "earliest end": lambda iv: iv[1],
    }
    for name, data in cases.items():
        best = max_activities(data)
        if name == "fewest conflicts":
            def conflicts(iv, data=data):
                # overlaps with every OTHER interval (an interval always overlaps itself once)
                return sum(1 for o in data if o[0] < iv[1] and iv[0] < o[1]) - 1
            got = greedy_by(data, key=lambda iv: (conflicts(iv), iv))
        else:
            got = greedy_by(data, rules[name])
        print(f"rule {name:<16} picks {got}, optimum is {best}")
    print()
    print("edge: empty      ->", max_activities([]), min_removals([]))
    print("edge: touching   ->", max_activities([(1, 2), (2, 3), (3, 4)]))
    print("edge: identical  ->", max_activities([(1, 5)] * 4), "removals", min_removals([(1, 5)] * 4))


if __name__ == "__main__":
    main()
