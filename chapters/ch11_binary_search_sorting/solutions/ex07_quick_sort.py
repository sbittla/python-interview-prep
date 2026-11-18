"""
Exercise 07 — Quick Sort and Partition Schemes                     [Tier: ★ Core]
Chapter 11 · Pattern: partition around a pivot · Target time: 25 min

Problem
-------
(a) Implement in-place quick sort with a random pivot (Lomuto partition).
(b) Implement Hoare partition and a quick sort that uses it.
(c) Implement three-way (Dutch national flag) partition and use it to sort a
list containing only 0s, 1s and 2s in one pass ("sort colours").

Examples
--------
>>> solve([3, 6, 1, 8, 2, 9, 2])
[1, 2, 2, 3, 6, 8, 9]
>>> sort_colors([2, 0, 2, 1, 1, 0])
[0, 0, 1, 1, 2, 2]

Constraints
-----------
- 0 <= len(nums) <= 10^5. Values may repeat heavily.

Approach ladder
---------------
1. Naive quick sort — first element as pivot, list comprehensions for the
   partitions. Easy to write; O(n^2) on sorted input; O(n) extra space per level.
2. Improved   — in-place Lomuto with a RANDOM pivot: expected O(n log n),
   O(log n) expected stack. Still O(n^2) when all keys are equal.
3. Optimal    — three-way partition (< pivot | == pivot | > pivot): equal keys
   are finished in one pass, so many duplicates become O(n). Hoare partition
   does fewer swaps than Lomuto.

Follow-ups
----------
- Quick sort is not stable. Why? Partition swaps jump elements past equals.
- Worst-case guarantee? Introsort (quick sort that falls back to heap sort).
- Recurse on the smaller side first and loop on the larger to bound the stack
  at O(log n) even in bad cases.
"""
from __future__ import annotations

import random


def naive_quick_sort(nums: list) -> list:
    if len(nums) <= 1:
        return list(nums)
    pivot = nums[0]
    return (naive_quick_sort([x for x in nums[1:] if x < pivot]) + [pivot]
            + naive_quick_sort([x for x in nums[1:] if x >= pivot]))


def partition_lomuto(a: list, lo: int, hi: int) -> int:
    """Pivot = a[hi]. After the call: a[lo:p] < pivot, a[p] == pivot, a[p+1:hi+1] >= pivot.
    Invariant during the loop: a[lo:i] < pivot and a[i:j] >= pivot."""
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i


def quick_sort_lomuto(a: list, lo: int = 0, hi: int | None = None,
                      rng: random.Random | None = None) -> None:
    if hi is None:
        hi = len(a) - 1
    if rng is None:
        rng = random.Random(0)
    while lo < hi:
        r = rng.randint(lo, hi)              # random pivot defeats sorted-input worst case
        a[r], a[hi] = a[hi], a[r]
        p = partition_lomuto(a, lo, hi)
        if p - lo < hi - p:                  # recurse on smaller side, loop on larger
            quick_sort_lomuto(a, lo, p - 1, rng)
            lo = p + 1
        else:
            quick_sort_lomuto(a, p + 1, hi, rng)
            hi = p - 1


def partition_hoare(a: list, lo: int, hi: int) -> int:
    """Pivot = middle value. Returns j such that a[lo..j] <= pivot <= a[j+1..hi].
    The pivot is NOT necessarily at index j."""
    pivot = a[(lo + hi) // 2]
    i, j = lo - 1, hi + 1
    while True:
        i += 1
        while a[i] < pivot:
            i += 1
        j -= 1
        while a[j] > pivot:
            j -= 1
        if i >= j:
            return j
        a[i], a[j] = a[j], a[i]


def quick_sort_hoare(a: list, lo: int = 0, hi: int | None = None) -> None:
    if hi is None:
        hi = len(a) - 1
    if lo < hi:
        p = partition_hoare(a, lo, hi)
        quick_sort_hoare(a, lo, p)           # note: p, not p - 1
        quick_sort_hoare(a, p + 1, hi)


def partition_3way(a: list, lo: int, hi: int, pivot) -> tuple[int, int]:
    """Dutch national flag. Afterwards a[lo:lt] < pivot, a[lt:gt+1] == pivot, a[gt+1:hi+1] > pivot.
    Invariant: a[lo:lt] < p, a[lt:i] == p, a[i:gt+1] unknown, a[gt+1:hi+1] > p."""
    lt, i, gt = lo, lo, hi
    while i <= gt:
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            lt += 1
            i += 1
        elif a[i] > pivot:
            a[i], a[gt] = a[gt], a[i]
            gt -= 1                          # do NOT advance i: the swapped-in value is unknown
        else:
            i += 1
    return lt, gt


def quick_sort_3way(a: list, lo: int = 0, hi: int | None = None,
                    rng: random.Random | None = None) -> None:
    if hi is None:
        hi = len(a) - 1
    if rng is None:
        rng = random.Random(0)
    if lo >= hi:
        return
    lt, gt = partition_3way(a, lo, hi, a[rng.randint(lo, hi)])
    quick_sort_3way(a, lo, lt - 1, rng)
    quick_sort_3way(a, gt + 1, hi, rng)


def sort_colors(nums: list[int]) -> list[int]:
    a = list(nums)
    partition_3way(a, 0, len(a) - 1, 1)
    return a


def solve(nums: list) -> list:
    a = list(nums)
    quick_sort_3way(a)
    return a


def main() -> None:
    data = [3, 6, 1, 8, 2, 9, 2]
    a = list(data)
    p = partition_lomuto(a, 0, len(a) - 1)
    print(f"Lomuto partition of {data} around pivot {data[-1]}: {a}, pivot index {p}")
    b = list(data)
    j = partition_hoare(b, 0, len(b) - 1)
    print(f"Hoare partition of {data} around pivot {data[len(data) // 2]}: {b}, split after {j}")
    c = [2, 1, 2, 3, 2, 0, 2]
    lt, gt = partition_3way(c, 0, len(c) - 1, 2)
    print(f"3-way partition of [2, 1, 2, 3, 2, 0, 2] around 2: {c}, equal block [{lt}..{gt}]")
    rng = random.Random(42)
    sample = [rng.randint(0, 50) for _ in range(15)]
    print("sample:", sample)
    x = list(sample); quick_sort_lomuto(x)
    y = list(sample); quick_sort_hoare(y)
    print("lomuto :", x)
    print("hoare  :", y)
    print("3-way  :", solve(sample))
    print("naive  :", naive_quick_sort(sample))
    print("all agree with sorted():", x == y == solve(sample) == sorted(sample))
    print("sort colours:", sort_colors([2, 0, 2, 1, 1, 0]))
    print("all equal:", solve([7] * 6), " empty:", solve([]), " one:", solve([4]))
    big_sorted = list(range(3000))
    z = list(big_sorted); quick_sort_lomuto(z)
    print("sorted input of 3000 with random pivot ok:", z == big_sorted)


if __name__ == "__main__":
    main()
