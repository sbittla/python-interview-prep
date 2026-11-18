"""
Exercise 12 — Sort-Based Patterns: Comparators, Sort Then Scan     [Tier: ★ Core]
Chapter 11 · Pattern: sort by a key, then a linear scan · Target time: 25 min

Problem
-------
(a) Largest number: arrange non-negative integers so their concatenation is
the largest possible number; return it as a string ("0" rather than "000").
(b) Merge intervals: merge all overlapping [start, end] intervals (touching
intervals such as [1,4] and [4,5] merge).
(c) Multi-key sort: sort (name, dept, salary) records by dept ascending, then
salary descending, then name ascending.
(d) Citation index: given citation counts, return the largest h such that at
least h papers have >= h citations each.

Examples
--------
>>> solve([3, 30, 34, 5, 9])
'9534330'
>>> merge_intervals([[1, 3], [8, 10], [2, 6], [15, 18]])
[[1, 6], [8, 10], [15, 18]]
>>> h_index([3, 0, 6, 1, 5])
3

Constraints
-----------
- 0 <= len(input) <= 10^4.

Approach ladder
---------------
(a) 1. Try every permutation: O(n! * n). 2. Sort by str descending: WRONG
    ("3" vs "30" gives "303" not "330"). 3. Sort with comparator
    a+b vs b+a via functools.cmp_to_key: O(n log n * L).
(b) 1. Compare every pair repeatedly until no merges: O(n^2) or worse.
    2. Sort by start, then one scan extending the last merged interval: O(n log n).
(d) 1. Try every h from n down: O(n^2). 2. Sort descending, scan: O(n log n).
    3. Counting buckets capped at n: O(n).

Follow-ups
----------
- Why is the comparator in (a) a valid total order? (a+b > b+a is transitive;
  well-known but worth stating rather than proving in an interview.)
- Python's sort is stable, so multi-key sorts can also be done as several
  passes from the least to the most important key.
- Insert an interval into a sorted, non-overlapping list in O(n) (Ch. 17).
"""
from __future__ import annotations

from functools import cmp_to_key
from itertools import permutations
from operator import itemgetter


def brute_force(nums: list[int]) -> str:
    if not nums:
        return ""
    best = max("".join(map(str, p)) for p in permutations(nums))
    return "0" if best[0] == "0" else best


def solve(nums: list[int]) -> str:
    """Largest number by concatenation."""
    strs = [str(x) for x in nums]

    def cmp(a: str, b: str) -> int:
        if a + b > b + a:
            return -1                 # a should come first
        if a + b < b + a:
            return 1
        return 0

    strs.sort(key=cmp_to_key(cmp))
    result = "".join(strs)
    return "0" if result and result[0] == "0" else result


def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals, key=itemgetter(0)):
        if merged and start <= merged[-1][1]:          # overlaps (or touches) the last one
            merged[-1][1] = max(merged[-1][1], end)     # max: the new one may be nested
        else:
            merged.append([start, end])
    return merged


def sort_employees(rows: list[tuple[str, str, int]]) -> list[tuple[str, str, int]]:
    # Tuple key: negate numbers to reverse just that component.
    return sorted(rows, key=lambda r: (r[1], -r[2], r[0]))


def sort_employees_multipass(rows: list[tuple[str, str, int]]) -> list[tuple[str, str, int]]:
    # Stable sort: apply keys from least to most significant.
    out = sorted(rows, key=itemgetter(0))
    out.sort(key=itemgetter(2), reverse=True)
    out.sort(key=itemgetter(1))
    return out


def h_index(citations: list[int]) -> int:
    c = sorted(citations, reverse=True)
    h = 0
    while h < len(c) and c[h] >= h + 1:
        h += 1
    return h


def h_index_counting(citations: list[int]) -> int:
    n = len(citations)
    buckets = [0] * (n + 1)
    for x in citations:
        buckets[min(x, n)] += 1
    papers = 0
    for h in range(n, -1, -1):
        papers += buckets[h]
        if papers >= h:
            return h
    return 0


def main() -> None:
    for nums in ([10, 2], [3, 30, 34, 5, 9], [0, 0], [1], [121, 12]):
        print(f"largest number {nums}: {solve(nums)!r} brute={brute_force(nums)!r}")
    wrong = "".join(sorted(map(str, [3, 30, 34, 5, 9]), reverse=True))
    print("wrong (plain string sort):", wrong)
    print("merge:", merge_intervals([[1, 3], [8, 10], [2, 6], [15, 18]]))
    print("merge touching:", merge_intervals([[1, 4], [4, 5]]))
    print("merge nested:", merge_intervals([[1, 10], [2, 3], [4, 5]]))
    print("merge empty:", merge_intervals([]))
    rows = [("eve", "ops", 90), ("bob", "eng", 120), ("amy", "eng", 120),
            ("dan", "ops", 95), ("cal", "eng", 100)]
    print("tuple key :", sort_employees(rows))
    print("multipass :", sort_employees_multipass(rows))
    for c in ([3, 0, 6, 1, 5], [1, 3, 1], [0, 0], [100], []):
        print(f"h-index {c}: sort={h_index(c)} counting={h_index_counting(c)}")


if __name__ == "__main__":
    main()
