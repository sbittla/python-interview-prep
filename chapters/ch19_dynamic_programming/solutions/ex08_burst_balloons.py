"""
Exercise 08 — Burst Balloons (interval DP)                          [Tier: ◆ Extended]
Chapter 19 · Pattern: interval DP, "last action in the interval" · Target time: 40 min

Problem
-------
Balloons in a row carry positive numbers nums[i]. Bursting balloon i earns
left * nums[i] * right, where left and right are its CURRENT neighbours (a missing
neighbour counts as 1); the balloon then disappears and its neighbours become adjacent.
Burst all balloons in the order that earns the most coins; return that total.

Examples
--------
>>> max_coins([3, 1, 5, 8])
167
>>> max_coins([1, 5]), max_coins([])
(10, 0)

Constraints
-----------
- 0 <= len(nums) <= 300, 0 <= nums[i] <= 100.

Approach ladder
---------------
1. Plain recursion over burst orders — try each balloon as the NEXT burst: O(n!) time.
2. Memo on the set of remaining balloons — 2^n subsets, O(n) choices each:
   O(2^n * n) time and space. Better, still exponential; the "first burst" state does
   not split into independent halves because neighbours change.
3. Interval DP, top-down — the insight: choose the LAST balloon k to burst inside the
   open interval (l, r). While the interval is being cleared, l and r are still there,
   and k is still there until the end, so the two sides are independent:
   best(l, r) = max over l < k < r of vals[l]*vals[k]*vals[r] + best(l, k) + best(k, r),
   with vals = [1] + nums + [1]; base best(l, l+1) = 0; answer best(0, n+1).
   O(n^3) time, O(n^2) space.
4. Bottom-up — fill by interval length (gap = r - l) ascending: O(n^3) time, O(n^2)
   space. No rolling-array saving: a cell reads cells of every shorter length.

Hints
-----
- "Which one first?" leads to dependent subproblems; ask "which one last?".
- Pad with 1s so the borders need no special case.
- Interval DP order: length 2, 3, ... (or l descending, r ascending).

Follow-ups
----------
- Matrix-chain multiplication and "minimum cost to cut a stick" use the same recurrence.
- Reconstruct the order: store the argmax k per interval, then emit sides before k.
"""
from __future__ import annotations

from functools import cache


def max_coins_brute(nums: list[int]) -> int:
    def best(balloons: tuple[int, ...]) -> int:
        top = 0
        for k, x in enumerate(balloons):
            left = balloons[k - 1] if k > 0 else 1
            right = balloons[k + 1] if k + 1 < len(balloons) else 1
            top = max(top, left * x * right + best(balloons[:k] + balloons[k + 1:]))
        return top

    return best(tuple(nums))


def max_coins_subset_memo(nums: list[int]) -> int:
    n = len(nums)

    @cache
    def best(mask: int) -> int:                 # bit i set = balloon i still present
        alive = [i for i in range(n) if mask >> i & 1]
        top = 0
        for pos, i in enumerate(alive):
            left = nums[alive[pos - 1]] if pos > 0 else 1
            right = nums[alive[pos + 1]] if pos + 1 < len(alive) else 1
            top = max(top, left * nums[i] * right + best(mask & ~(1 << i)))
        return top

    return best((1 << n) - 1)


def max_coins_memo(nums: list[int]) -> int:
    vals = [1] + nums + [1]

    @cache
    def best(l: int, r: int) -> int:            # burst everything strictly between l and r
        return max((vals[l] * vals[k] * vals[r] + best(l, k) + best(k, r)
                    for k in range(l + 1, r)), default=0)

    return best(0, len(vals) - 1)


def max_coins(nums: list[int]) -> int:
    vals = [1] + nums + [1]
    m = len(vals)
    best = [[0] * m for _ in range(m)]
    for gap in range(2, m):                     # interval length, shortest first
        for l in range(0, m - gap):
            r = l + gap
            best[l][r] = max(vals[l] * vals[k] * vals[r] + best[l][k] + best[k][r]
                             for k in range(l + 1, r))
    return best[0][m - 1]


def main() -> None:
    for nums in ([3, 1, 5, 8], [1, 5], [7], [], [2, 4, 3, 5, 1, 6]):
        rungs = (max_coins_brute(nums), max_coins_subset_memo(nums), max_coins_memo(nums),
                 max_coins(nums))
        print(f"max_coins({nums}) = {rungs[-1]}  rungs agree: {len(set(rungs)) == 1}")
    nums = [(i * 37) % 100 + 1 for i in range(100)]
    print("n=100, top-down == bottom-up:", max_coins_memo(nums) == max_coins(nums))


if __name__ == "__main__":
    main()
