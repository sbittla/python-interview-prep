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

Hints
-----
- Bit i of ``mask`` set <=> nums[i] is in the subset: ``mask >> i & 1``.
- ``mask & -mask`` isolates the lowest set bit; its index is ``bit_length() - 1``.
- ``(sub - 1) & mask`` is the next smaller submask; stop after emitting 0.
- Gosper: add the lowest set bit to carry the lowest block of 1s, then refill the low end.

Wrong-but-tempting
------------------
- ``while sub:`` as the submask loop condition: drops the empty submask.
- ``1 << n - 1`` means ``1 << (n - 1)``: shifts bind looser than ``-``.
- Iterating all 2**n masks per mask to find submasks: O(4**n) instead of O(3**n).

Follow-ups
----------
- Duplicates in nums? Bitmask enumeration repeats subsets; dedupe by sorted tuple or use
  backtracking with skip (Chapter 18, ex02).
- Meet in the middle: subset sums of two halves, sort one, binary search — O(2**(n/2) n).
"""
from __future__ import annotations


def subsets(nums: list[int]) -> list[list[int]]:
    raise NotImplementedError("TODO")


def subset_sums_brute(nums: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def subset_sums(nums: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def submasks(mask: int) -> list[int]:
    raise NotImplementedError("TODO")


def k_subset_masks(n: int, k: int) -> list[int]:
    raise NotImplementedError("TODO")


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
