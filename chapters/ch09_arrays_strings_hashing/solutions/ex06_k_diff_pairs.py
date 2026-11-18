"""
Exercise 06 — Count Distinct K-Difference Pairs          [Tier: ★ Core]
Chapter 09 · Pattern: two-sum family (hash map / Counter) · Target time: 15 min

Problem
-------
Given a list of integers nums and an integer k >= 0, count the distinct value
pairs (a, b) with a <= b, b - a == k, where a and b come from two different
positions of nums. Pairs are counted by value, so duplicates in the input do not
create extra pairs.

Examples
--------
>>> solve([3, 1, 4, 1, 5], 2)      # (1, 3) and (3, 5)
2
>>> solve([1, 3, 1, 5, 4], 0)      # (1, 1) only
1

Constraints
-----------
- 0 <= k; len(nums) <= 10**5; values may be negative.

Approach ladder
---------------
1. Brute force — test every index pair, store value pairs in a set. O(n^2).
2. Improved   — sort, then two pointers or binary search for x + k. O(n log n).
3. Optimal    — Counter of values. For k > 0 count values x with x + k present.
   For k == 0 count values that appear at least twice. O(n) time, O(n) space.
   The k == 0 split is the whole trick: "x + 0 in counts" is always true.

Follow-ups
----------
- Count index pairs instead of value pairs: sum counts[x] * counts[x + k].
- Two-sum variant "count pairs with sum == target": same Counter idea, careful
  with x == target - x.
- Absolute difference with negative k? Define k = abs(k) first.
"""
from __future__ import annotations

from collections import Counter


def brute_force(nums: list[int], k: int) -> int:
    pairs = set()
    for i in range(len(nums)):
        for j in range(len(nums)):
            if i != j and nums[j] - nums[i] == k:
                pairs.add((nums[i], nums[j]))
    return len(pairs)


def wrong_set_only(nums: list[int], k: int) -> int:
    """Wrong-but-tempting: forgets that k == 0 needs a duplicate."""
    values = set(nums)
    return sum(1 for x in values if x + k in values)


def solve(nums: list[int], k: int) -> int:
    if k < 0:
        return 0
    counts = Counter(nums)
    if k == 0:
        return sum(1 for c in counts.values() if c >= 2)
    return sum(1 for x in counts if x + k in counts)


def main() -> None:
    cases = [([3, 1, 4, 1, 5], 2), ([1, 2, 3, 4, 5], 1), ([1, 3, 1, 5, 4], 0),
             ([1, 2, 3], 0), ([], 3), ([-1, -3, 1], 2)]
    for nums, k in cases:
        print(f"nums={nums!s:<17} k={k} -> {solve(nums, k)}"
              f"  brute={brute_force(nums, k)}  set-only(wrong)={wrong_set_only(nums, k)}")


if __name__ == "__main__":
    main()
