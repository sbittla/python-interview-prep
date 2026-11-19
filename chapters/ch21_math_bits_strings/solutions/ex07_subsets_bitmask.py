"""
Exercise 07 — Subsets via Bitmask, Submasks, Subset Sums        [Tier: ★ Core]
Chapter 21 · Pattern: integer as a set of indices · Target time: 20 min

Problem
-------
1. ``subsets(nums)``: all 2**n subsets; subset number ``mask`` holds nums[i] exactly when bit
   i of mask is set (so the output is ordered by mask: [], [a], [b], [a, b], ...).
2. ``subset_sums(nums)``: list where entry ``mask`` is the sum of that subset.
3. ``submasks(mask)``: every submask of mask, descending, including mask and 0.
4. ◆ ``k_subset_masks(n, k)``: all n-bit masks with exactly k set bits, ascending
   (Gosper's hack).

Examples
--------
>>> subsets([1, 2, 3])
[[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
>>> submasks(0b101)
[5, 4, 1, 0]
>>> [bin(m) for m in k_subset_masks(4, 2)][:3]
['0b11', '0b101', '0b110']

Constraints
-----------
- n <= 20 (2**20 ≈ 10**6 subsets). Backtracking view of the same problem: Chapter 18 (§18.2);
  DP over masks: §19.13.

Approach ladder
---------------
subset_sums:
1. Brute force — for each mask, add up its members. O(n 2**n).
2. Optimal    — sums[mask] = sums[mask without its lowest bit] + nums[index of that bit]:
   ``low = mask & -mask``; index ``low.bit_length() - 1``. O(2**n) time and space.
   Why move up: each sum reuses one already computed.
submasks: ``sub = (sub - 1) & mask`` steps to the next smaller submask: O(2**popcount(mask))
per mask; summed over all masks of n bits that is O(3**n), not O(4**n).
k-subsets: filtering all masks by popcount costs O(2**n); Gosper jumps straight to the next
mask with the same popcount, O(C(n, k)) masks generated.

Follow-ups
----------
- Duplicates in nums? Bitmask enumeration repeats subsets; dedupe by sorted tuple or use
  backtracking with skip (Chapter 18, ex02).
- Meet in the middle: subset sums of two halves, sort one, binary search — O(2**(n/2) n).
"""
from __future__ import annotations


def subsets(nums: list[int]) -> list[list[int]]:
    n = len(nums)
    return [[nums[i] for i in range(n) if mask >> i & 1] for mask in range(1 << n)]


def subset_sums_brute(nums: list[int]) -> list[int]:
    return [sum(s) for s in subsets(nums)]


def subset_sums(nums: list[int]) -> list[int]:
    sums = [0] * (1 << len(nums))
    for mask in range(1, 1 << len(nums)):
        low = mask & -mask                       # lowest set bit
        sums[mask] = sums[mask ^ low] + nums[low.bit_length() - 1]
    return sums


def submasks(mask: int) -> list[int]:
    out, sub = [], mask
    while True:
        out.append(sub)
        if sub == 0:
            return out
        sub = (sub - 1) & mask


def k_subset_masks(n: int, k: int) -> list[int]:
    if k < 0 or k > n:
        return []
    if k == 0:
        return [0]
    out, x, limit = [], (1 << k) - 1, 1 << n
    while x < limit:
        out.append(x)
        c = x & -x                               # lowest set bit
        r = x + c                                # carry ripples through the lowest 1-block
        x = (((r ^ x) >> 2) // c) | r            # refill the low end with the lost 1s
    return out


def main() -> None:
    print("subsets([1, 2, 3]) =", subsets([1, 2, 3]))
    print("subsets([])        =", subsets([]))
    nums = [3, 5, 9]
    print("subset_sums", nums, "=", subset_sums(nums), " brute agrees:", subset_sums(nums) == subset_sums_brute(nums))
    print("submasks(0b1011)   =", [f"{m:04b}" for m in submasks(0b1011)])
    print("k_subset_masks(5, 3) =", [f"{m:05b}" for m in k_subset_masks(5, 3)])
    total = sum(len(submasks(m)) for m in range(1 << 6))
    print("sum of submask counts over all 6-bit masks =", total, " 3**6 =", 3**6)


if __name__ == "__main__":
    main()
