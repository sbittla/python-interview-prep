"""
Exercise 12 — Batch Range Updates with a Difference Array  [Tier: ◆ Extended]
Chapter 10 · Pattern: difference array (inverse of prefix sums) · Target time: 15 min

Problem
-------
solve(n, updates): start from n zeros; each update (lo, hi, delta) adds delta
to every position lo..hi inclusive. Return the final array.
peak_load(trips): each trip (passengers, start, end) occupies a vehicle on
the half-open stretch [start, end). Return the maximum number of passengers
on board at any point (0 for no trips).

Examples
--------
>>> solve(5, [(1, 3, 2), (2, 4, 3), (0, 2, -2)])
[-2, 0, 3, 5, 3]
>>> peak_load([(2, 1, 5), (3, 3, 7)])
5

Constraints
-----------
- 1 <= n <= 10**5; up to 10**5 updates; 0 <= lo <= hi < n.
- peak_load: 0 <= start < end <= 1000.

Approach ladder
---------------
1. Brute force — loop over lo..hi for every update. O(n * q) worst case.
2. Optimal    — record only the boundaries: diff[lo] += delta and
   diff[hi + 1] -= delta (diff has n + 1 slots so hi + 1 never overflows).
   The running prefix sum of diff is the final array. O(n + q) time,
   O(n) space. A difference array is the inverse of a prefix sum: prefix
   sums answer many range QUERIES on fixed data; difference arrays apply
   many range UPDATES and read the data once at the end.
   (For a sparse or huge coordinate range, sort the boundary events
   instead: O(q log q), independent of n — a sweep line, see Chapter 17.)

Wrong-but-tempting
------------------
- Using the inclusive formula for half-open intervals (or vice versa):
  the passengers of a trip ending at x leave AT x, so subtract at end, not
  end + 1. Getting this wrong over-counts at shared stops.
- Interleaving queries with updates: the array is only correct after the
  final prefix pass; online mixing needs a Fenwick tree (-> Chapter 22.9).

Follow-ups
----------
- 2D difference array: +d at (r1, c1), -d at (r1, c2+1) and (r2+1, c1),
  +d at (r2+1, c2+1); then 2D prefix sums.
- Can a vehicle of capacity C serve all trips? peak_load(trips) <= C.
"""
from __future__ import annotations

from itertools import accumulate


def brute_force(n: int, updates: list[tuple[int, int, int]]) -> list[int]:
    arr = [0] * n
    for lo, hi, delta in updates:
        for i in range(lo, hi + 1):
            arr[i] += delta
    return arr


def solve(n: int, updates: list[tuple[int, int, int]]) -> list[int]:
    diff = [0] * (n + 1)                  # one spare slot for hi + 1
    for lo, hi, delta in updates:
        diff[lo] += delta
        diff[hi + 1] -= delta
    return list(accumulate(diff[:n]))


def peak_load_brute(trips: list[tuple[int, int, int]]) -> int:
    stops = range(min((s for _, s, _ in trips), default=0), max((e for _, _, e in trips), default=0))
    return max((sum(p for p, s, e in trips if s <= x < e) for x in stops), default=0)


def wrong_inclusive_end(trips: list[tuple[int, int, int]]) -> int:
    """Wrong-but-tempting: treats [start, end) as inclusive of end."""
    if not trips:
        return 0
    diff = [0] * (max(e for _, _, e in trips) + 2)
    for p, s, e in trips:
        diff[s] += p
        diff[e + 1] -= p                  # bug: passengers left AT e
    return max(accumulate(diff))


def peak_load(trips: list[tuple[int, int, int]]) -> int:
    if not trips:
        return 0
    size = max(e for _, _, e in trips)
    # half-open [s, e) is the inclusive range s..e-1
    return max(solve(size, [(s, e - 1, p) for p, s, e in trips]))


def main() -> None:
    cases = [(5, [(1, 3, 2), (2, 4, 3), (0, 2, -2)]), (3, []), (4, [(0, 3, 1), (3, 3, 4)])]
    for n, updates in cases:
        print(f"n={n} updates={updates!s:<34} -> {solve(n, updates)}"
              f"  brute agrees: {solve(n, updates) == brute_force(n, updates)}")
    for trips in [[(2, 1, 5), (3, 3, 7)], [(2, 1, 5), (3, 5, 7)], [(3, 2, 7), (3, 7, 9), (8, 3, 9)], []]:
        print(f"trips={trips!s:<34} -> peak {peak_load(trips):<2} brute={peak_load_brute(trips):<2}"
              f" inclusive-end(wrong)={wrong_inclusive_end(trips)}")


if __name__ == "__main__":
    main()
