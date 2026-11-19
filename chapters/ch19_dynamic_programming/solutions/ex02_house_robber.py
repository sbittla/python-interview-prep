"""
Exercise 02 — House Robber: Line and Circle                         [Tier: ★ Core]
Chapter 19 · Pattern: 1D DP, take/skip · Target time: 25 min

Problem
-------
Houses stand in a row; nums[i] >= 0 is the cash in house i. Robbing two adjacent
houses trips the alarm.
1. `rob(nums)` — the most cash you can take from the row.
2. `rob_with_houses(nums)` — the same total plus the (sorted) indices of one optimal
   set of houses.
3. `rob_circular(nums)` — the houses stand in a circle, so the first and last are
   adjacent too.

Examples
--------
>>> rob([2, 7, 9, 3, 1])
12
>>> rob_with_houses([2, 7, 9, 3, 1])
(12, [0, 2, 4])
>>> rob_circular([2, 3, 2]), rob_circular([1, 2, 3, 1])
(3, 4)

Constraints
-----------
- 0 <= len(nums) <= 10^5, 0 <= nums[i] <= 10^4. Empty input returns 0 (and []).

Approach ladder
---------------
DP recipe — state: best(i) = most cash from the first i houses; transition:
best(i) = max(best(i-1), nums[i-1] + best(i-2)) (skip house i-1, or take it and skip
its neighbour); base: best(0) = 0, best(-1) = 0; order: i ascending; answer: best(n).
1. Plain recursion — two calls per house: O(phi^n) ~ O(1.618^n) time, O(n) stack.
2. Memoised — n states, O(1) work each: O(n) time, O(n) space + O(n) stack.
3. Bottom-up table — O(n) time, O(n) space; keeps enough to reconstruct the houses.
4. Two variables — best(i) reads only best(i-1), best(i-2): O(n) time, O(1) space,
   but the reconstruction is gone (keep the table if you must list the houses).
Circle: house 0 and house n-1 cannot both be robbed, so answer
max(rob(nums[1:]), rob(nums[:-1])) — two linear runs, O(n). One house: take it.

Hints
-----
- At house i you have exactly two choices; write the max of them.
- To reconstruct, walk the table backwards: if best(i) == best(i-1) house i-1 was
  skipped, otherwise it was taken and you jump to i-2.
- For the circle, break it: some optimal answer skips house 0 or skips house n-1.

Follow-ups
----------
- Houses on a binary tree (exercise 10, section 19.12).
- "Delete and earn": bucket equal values, then it is this problem on the value line.
"""
from __future__ import annotations

from functools import cache


def rob_brute(nums: list[int]) -> int:
    def best(i: int) -> int:                    # first i houses
        if i <= 0:
            return 0
        return max(best(i - 1), nums[i - 1] + best(i - 2))

    return best(len(nums))


def rob_memo(nums: list[int]) -> int:
    @cache
    def best(i: int) -> int:
        if i <= 0:
            return 0
        return max(best(i - 1), nums[i - 1] + best(i - 2))

    return best(len(nums))


def _table(nums: list[int]) -> list[int]:
    best = [0] * (len(nums) + 1)
    for i in range(1, len(nums) + 1):
        best[i] = max(best[i - 1], nums[i - 1] + (best[i - 2] if i >= 2 else 0))
    return best


def rob_table(nums: list[int]) -> int:
    return _table(nums)[-1]


def rob(nums: list[int]) -> int:
    prev2 = prev1 = 0                           # best(i - 2), best(i - 1)
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1


def rob_with_houses(nums: list[int]) -> tuple[int, list[int]]:
    best = _table(nums)
    chosen, i = [], len(nums)
    while i > 0:
        if best[i] == best[i - 1]:              # house i-1 skipped
            i -= 1
        else:                                   # house i-1 taken
            chosen.append(i - 1)
            i -= 2
    return best[-1], chosen[::-1]


def rob_circular_brute(nums: list[int]) -> int:
    """Try every subset of houses (O(2^n * n)); reject any with adjacent pairs."""
    n, best = len(nums), 0
    for mask in range(1 << n):
        if any(mask >> i & 1 and mask >> ((i + 1) % n) & 1 and (i + 1) % n != i
               for i in range(n)):
            continue
        best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


def rob_circular(nums: list[int]) -> int:
    if len(nums) == 1:
        return nums[0]
    return max(rob(nums[1:]), rob(nums[:-1]))


def main() -> None:
    for nums in ([2, 7, 9, 3, 1], [1, 2, 3, 1], [2, 1, 1, 2], [5], []):
        rungs = (rob_brute(nums), rob_memo(nums), rob_table(nums), rob(nums))
        print(f"rob({nums}) = {rob(nums):<3} with houses {rob_with_houses(nums)[1]}"
              f"  rungs agree: {len(set(rungs)) == 1}")
    for nums in ([2, 3, 2], [1, 2, 3, 1], [1, 2, 3], [200, 3, 140, 20, 10], [7]):
        print(f"rob_circular({nums}) = {rob_circular(nums)}  brute = {rob_circular_brute(nums)}")


if __name__ == "__main__":
    main()
