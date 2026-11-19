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

Approach ladder
---------------
Grade:
1. Brute force — an if/elif chain or a linear scan over cut-offs: O(bands).
2. Optimal    — `bisect_right(cutoffs, score)` IS the band index: O(log bands).
   bisect_right puts a score equal to a cut-off in the higher band.
Leaderboard:
1. Brute force — unsorted list; each query scans it: O(n) per query.
2. Improved   — `append` then `sort` on every add: O(n log n) per add.
3. Optimal    — `insort` keeps the list sorted: O(log n) search + O(n) shift
   (a fast memmove); queries are two binary searches, O(log n).
   For truly heavy insert loads use a balanced tree / sortedcontainers.

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
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def grade(score: int) -> str:
    return LETTERS[bisect_right(CUTOFFS, score)]


class Leaderboard:
    def __init__(self) -> None:
        self.scores: list[int] = []            # always sorted ascending

    def add(self, score: int) -> None:
        insort(self.scores, score)             # O(log n) search + O(n) shift

    def rank(self, score: int) -> int:
        return len(self.scores) - bisect_right(self.scores, score) + 1

    def count_between(self, lo: int, hi: int) -> int:
        if lo > hi:
            return 0
        return bisect_right(self.scores, hi) - bisect_left(self.scores, lo)


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
