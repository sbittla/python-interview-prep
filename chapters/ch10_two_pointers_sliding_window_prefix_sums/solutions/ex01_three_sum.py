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

Approach ladder
---------------
1. Brute force — every combination of three positions, keep sorted triplets
   that sum to 0 in a set. O(n^3) time.
2. Improved   — fix i, then run a hash-set two-sum over the suffix for
   target -nums[i]. O(n^2) time, O(n) extra space; duplicates are removed by
   a set of tuples.
3. Optimal    — sort once (O(n log n)), fix i, then move lo/hi inward over the
   suffix: sum too small -> lo += 1, too big -> hi -= 1. Skip equal values at
   i and lo to emit each triplet once. O(n^2) time, O(1) extra space besides
   the sorted copy and the output. Sorting is what lets a pointer move
   *provably* discard candidates, and it makes de-duplication free.
   No O(n^(2-eps)) algorithm is known, so O(n^2) is the interview target.

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
    found = {tuple(sorted(t)) for t in combinations(nums, 3) if sum(t) == 0}
    return sorted(found)


def hash_two_sum(nums: list[int]) -> list[tuple[int, int, int]]:
    found: set[tuple[int, int, int]] = set()
    for i in range(len(nums)):
        seen: set[int] = set()
        for j in range(i + 1, len(nums)):
            need = -nums[i] - nums[j]
            if need in seen:
                found.add(tuple(sorted((nums[i], nums[j], need))))
            seen.add(nums[j])
    return sorted(found)


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
    nums = sorted(nums)
    n, out = len(nums), []
    for i in range(n - 2):
        if nums[i] > 0:                   # smallest value positive: done
            break
        if i > 0 and nums[i] == nums[i - 1]:
            continue                      # same anchor -> same triplets
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s < 0:
                lo += 1                   # need a bigger sum
            elif s > 0:
                hi -= 1                   # need a smaller sum
            else:
                out.append((nums[i], nums[lo], nums[hi]))
                lo += 1
                hi -= 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1               # skip duplicate middles
    return out


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
