"""
Exercise 02 — Jump Game I and II                                   [Tier: ★ Core]
Chapter 20 · Pattern: greedy reach / implicit BFS layers · Target time: 20 min

Problem
-------
`nums[i]` is the maximum jump length from index i (you may jump any distance 0..nums[i]).
1. `can_reach(nums)` — can you get from index 0 to the last index?
2. `min_jumps(nums)` — the fewest jumps to reach the last index, or -1 if impossible.

Examples
--------
>>> can_reach([2, 3, 1, 1, 4])
True
>>> can_reach([3, 2, 1, 0, 4])
False
>>> min_jumps([2, 3, 1, 1, 4])
2

Constraints
-----------
- 1 <= len(nums) <= 10^5, 0 <= nums[i] <= 10^5.

Approach ladder
---------------
1. Brute force — DP: reachable[i] / best[i] from every earlier j. O(n^2) time, O(n) space.
2. Optimal (I) — track the furthest index reachable so far; if i ever exceeds it, stop.
   O(n) time, O(1) space.
3. Optimal (II) — BFS by layers without a queue: [start, end] is the set of indices
   reachable with k jumps; the next layer ends at the furthest reach from that window.
   O(n) time, O(1) space.

Hints
-----
- You never need to know WHICH index you jumped from, only how far you can get.
- For II, think of indices reachable in exactly k jumps as one contiguous window.

Follow-ups
----------
- Jump Game III (jump exactly +-nums[i]): graph BFS/DFS, greedy does not apply.
- Return the actual jump path: record the index that achieved the furthest reach per layer.
"""
from __future__ import annotations


def can_reach_dp(nums: list[int]) -> bool:
    n = len(nums)
    ok = [False] * n
    ok[0] = True
    for i in range(1, n):
        ok[i] = any(ok[j] and j + nums[j] >= i for j in range(i))
    return ok[-1]


def can_reach(nums: list[int]) -> bool:
    furthest = 0
    for i, step in enumerate(nums):
        if i > furthest:            # index i is unreachable, so everything after is too
            return False
        furthest = max(furthest, i + step)
    return True


def min_jumps_dp(nums: list[int]) -> int:
    n = len(nums)
    inf = float("inf")
    best = [inf] * n
    best[0] = 0
    for i in range(1, n):
        for j in range(i):
            if j + nums[j] >= i and best[j] + 1 < best[i]:
                best[i] = best[j] + 1
    return -1 if best[-1] == inf else int(best[-1])


def min_jumps(nums: list[int], trace: bool = False) -> int:
    jumps, window_end, furthest = 0, 0, 0
    for i in range(len(nums) - 1):          # never jump FROM the last index
        furthest = max(furthest, i + nums[i])
        if i == window_end:                 # finished scanning layer `jumps`
            if furthest <= i:
                return -1                   # stuck: the next layer is empty
            jumps += 1
            window_end = furthest
            if trace:
                print(f"  layer {jumps}: indices up to {window_end}")
    return jumps


def main() -> None:
    for nums in ([2, 3, 1, 1, 4], [3, 2, 1, 0, 4], [0], [1, 0], [0, 1], [2, 0, 0], [1, 1, 1, 1]):
        print(f"{str(nums):<16} can_reach={can_reach(nums)!s:<5} (dp {can_reach_dp(nums)!s:<5})"
              f" min_jumps={min_jumps(nums):>2} (dp {min_jumps_dp(nums)})")
    print()
    nums = [2, 3, 1, 1, 2, 4, 2, 0, 1, 1]
    print("trace of min_jumps on", nums)
    print("answer:", min_jumps(nums, trace=True))


if __name__ == "__main__":
    main()
