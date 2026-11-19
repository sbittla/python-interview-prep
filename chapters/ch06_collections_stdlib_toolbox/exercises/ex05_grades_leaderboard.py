"""
Exercise 05 — Grade Bands and a Sorted Leaderboard with bisect  [Tier: ★ Core]
Chapter 06 · Pattern: bisect on a sorted list · Target time: 15 min

Problem
-------
1. `grade(score)` — map a score 0..100 to a letter: below 60 is F, [60, 70) D,
   [70, 80) C, [80, 90) B, 90 and above A. Boundaries belong to the HIGHER band.
2. `Leaderboard` — `add(score)` records a score (duplicates allowed);
   `rank(score)` returns 1 + the number of recorded scores strictly greater
   (ties share a rank; the score need not be recorded); `count_between(lo, hi)`
   counts recorded scores with lo <= s <= hi.

Examples
--------
>>> [grade(s) for s in (59, 60, 89, 90, 100)]
['F', 'D', 'B', 'A', 'A']
>>> lb = Leaderboard()
>>> for s in (50, 80, 80, 95):
...     lb.add(s)
>>> lb.rank(80), lb.count_between(60, 90)
(2, 2)

Constraints
-----------
- Up to 10**5 adds and 10**5 queries.

Hints
-----
- Strictly greater than s: len(scores) - bisect_right(scores, s).
- Inclusive range [lo, hi]: bisect_right(hi) - bisect_left(lo).

Follow-ups
----------
- Remove a score: `i = bisect_left(a, s)`; check `a[i] == s`; `del a[i]`.
- Records instead of numbers: `bisect`/`insort` take `key=` since Python 3.10.
"""
from __future__ import annotations

from bisect import bisect_left, bisect_right, insort

CUTOFFS = [60, 70, 80, 90]
LETTERS = "FDCBA"


def brute_force_grade(score: int) -> str:
    raise NotImplementedError("TODO")


def grade(score: int) -> str:
    raise NotImplementedError("TODO")


class Leaderboard:
    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def add(self, score: int) -> None:
        raise NotImplementedError("TODO")

    def rank(self, score: int) -> int:
        raise NotImplementedError("TODO")

    def count_between(self, lo: int, hi: int) -> int:
        raise NotImplementedError("TODO")


def main() -> None:
    for s in (0, 59, 60, 75, 89, 90, 100):
        print(f"grade({s:3}) = {grade(s)}  brute = {brute_force_grade(s)}")
    lb = Leaderboard()
    for s in (50, 80, 80, 95, 70):
        lb.add(s)
    print("scores:", lb.scores)
    print("rank(95) =", lb.rank(95), "| rank(80) =", lb.rank(80),
          "| rank(81) =", lb.rank(81), "| rank(10) =", lb.rank(10))
    print("count_between(70, 80) =", lb.count_between(70, 80),
          "| count_between(81, 94) =", lb.count_between(81, 94))
    a = [10, 20, 20, 30]
    print("bisect_left(a, 20) =", bisect_left(a, 20), "| bisect_right(a, 20) =", bisect_right(a, 20))


if __name__ == "__main__":
    main()
