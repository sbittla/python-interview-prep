"""
Exercise 13 — Longest Consecutive Run (set membership)    [Tier: ★ Core]
Chapter 09 · Pattern: set-based membership · Target time: 15 min

Problem
-------
Given an unsorted list of integers, return the length of the longest run of
consecutive integer values (e.g. 4, 5, 6, 7) that all appear in the list.
Order in the list does not matter and duplicates count once. Also implement
contains_duplicate(nums) -> bool.

Examples
--------
>>> solve([100, 4, 200, 1, 3, 2])
4
>>> solve([])
0

Constraints
-----------
- 0 <= len(nums) <= 10**5; values in [-10**9, 10**9].

Approach ladder
---------------
1. Brute force — for each x, count upwards while x+1 is in the *list*:
   O(n) membership per step -> O(n^3) worst case.
2. Improved   — sort, then scan counting runs and skipping duplicates.
   O(n log n) time.
3. Optimal    — put values in a set. Only start counting at x when x-1 is NOT in
   the set (x is a run start). Each value is visited by at most one inner loop,
   so the total work is O(n) even though there is a nested while.

Follow-ups
----------
- Return the run itself, not just its length.
- Streaming inserts: union-find or a dict of run endpoints (Chapter 16).
- Why is the nested loop still O(n)? Amortised argument: each element is the
  "next" of at most one run walk.
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> int:
    best = 0
    for x in nums:
        length = 1
        while x + length in nums:      # list membership: O(n)
            length += 1
        best = max(best, length)
    return best


def by_sorting(nums: list[int]) -> int:
    if not nums:
        return 0
    vals = sorted(set(nums))
    best = run = 1
    for a, b in zip(vals, vals[1:]):
        run = run + 1 if b == a + 1 else 1
        best = max(best, run)
    return best


def solve(nums: list[int]) -> int:
    values = set(nums)
    best = 0
    for x in values:
        if x - 1 in values:            # not a run start; someone else counts it
            continue
        y = x
        while y + 1 in values:
            y += 1
        best = max(best, y - x + 1)
    return best


def contains_duplicate(nums: list[int]) -> bool:
    return len(set(nums)) != len(nums)


def first_duplicate(nums: list[int]):
    """Early-exit variant: returns the first value seen twice, else None."""
    seen = set()
    for x in nums:
        if x in seen:
            return x
        seen.add(x)
    return None


def main() -> None:
    for nums in [[100, 4, 200, 1, 3, 2], [0, 3, 7, 2, 5, 8, 4, 6, 0, 1], [], [5], [1, 2, 0, 1], [-2, -1, 9]]:
        print(f"{nums!s:<32} longest={solve(nums)} brute={brute_force(nums)} sorted={by_sorting(nums)}")
    print("contains_duplicate([1,2,3,1]):", contains_duplicate([1, 2, 3, 1]))
    print("first_duplicate([2, 5, 1, 5, 2]):", first_duplicate([2, 5, 1, 5, 2]))
    a, b = {1, 2, 3, 4}, {3, 4, 5}
    print("intersection:", sorted(a & b), "union:", sorted(a | b), "a-b:", sorted(a - b), "xor:", sorted(a ^ b))


if __name__ == "__main__":
    main()
