"""
Exercise 01 — Three Sum to Zero (unique triplets)        [Tier: ★ Core]
Chapter 10 · Pattern: opposite-direction two pointers (sorted) · Target time: 20 min

Problem
-------
Given a list of integers nums, return every distinct value triplet (a, b, c)
with a <= b <= c and a + b + c == 0, where the three values come from three
different positions. Return the triplets as tuples in ascending lexicographic
order. Duplicates in the input must not produce duplicate triplets.

Examples
--------
>>> solve([-1, 0, 1, 2, -1, -4])
[(-1, -1, 2), (-1, 0, 1)]
>>> solve([0, 0, 0, 0])
[(0, 0, 0)]

Constraints
-----------
- 0 <= len(nums) <= 3000; values may be negative.

Hints
-----
- Sort first: equal values become neighbours and pointer moves become meaningful.
- Fix the smallest element i; find pairs in nums[i+1:] summing to -nums[i] with lo/hi.
- Skip an anchor equal to the PREVIOUS anchor; after a hit skip equal lo values.

Wrong-but-tempting
------------------
- Skipping duplicates of nums[i] with `nums[i] == nums[i + 1]` (look-ahead)
  instead of `nums[i] == nums[i - 1]` (look-back): it loses (-1, -1, 2).
- Forgetting to skip duplicates after a hit: emits the same triplet twice.

Follow-ups
----------
- 3-sum closest to a target: same loop, track the best |sum - target|.
- k-sum: recurse down to the two-pointer base case. O(n^(k-1)).
- Count triplets with sum < target: when the sum is small enough, all
  hi - lo pairs with this lo count at once.
"""
from __future__ import annotations

from itertools import combinations


def brute_force(nums: list[int]) -> list[tuple[int, int, int]]:
    raise NotImplementedError("TODO")


def hash_two_sum(nums: list[int]) -> list[tuple[int, int, int]]:
    raise NotImplementedError("TODO")


def wrong_lookahead_skip(nums: list[int]) -> list[tuple[int, int, int]]:
    """Wrong-but-tempting: skips nums[i] when the NEXT value is equal."""
    nums = sorted(nums)
    out = []
    for i in range(len(nums) - 2):
        if nums[i] == nums[i + 1]:
            continue                      # bug: should compare with nums[i - 1]
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s == 0:
                out.append((nums[i], nums[lo], nums[hi]))
                lo += 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
            elif s < 0:
                lo += 1
            else:
                hi -= 1
    return out


def solve(nums: list[int]) -> list[tuple[int, int, int]]:
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [[-1, 0, 1, 2, -1, -4], [0, 0, 0, 0], [1, 2, -2, -1], [], [0, 0],
             [-2, 0, 1, 1, 2], [-4, -1, -1, 0, 1, 2]]
    for nums in cases:
        print(f"nums={nums!s:<22} -> {solve(nums)}")
        print(f"{'':27}brute agrees: {brute_force(nums) == solve(nums)}"
              f"  hash agrees: {hash_two_sum(nums) == solve(nums)}"
              f"  lookahead-skip(wrong): {wrong_lookahead_skip(nums)}")


if __name__ == "__main__":
    main()
