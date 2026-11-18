"""
Exercise 02 — First and Last Position (Lower/Upper Bound)         [Tier: ★ Core]
Chapter 11 · Pattern: binary search boundaries / bisect · Target time: 15 min

Problem
-------
A sorted list may contain duplicates. Return [first, last], the first and last
indices at which target appears, or [-1, -1] if it does not appear. Also write
lower_bound (first index with nums[i] >= x) and upper_bound (first index with
nums[i] > x) by hand, and show they agree with bisect_left / bisect_right.

Examples
--------
>>> solve([1, 2, 2, 2, 5, 7], 2)
[1, 3]
>>> solve([1, 2, 2, 2, 5, 7], 4)
[-1, -1]
>>> lower_bound([1, 2, 2, 2, 5, 7], 4), upper_bound([1, 2, 2, 2, 5, 7], 2)
(4, 4)

Constraints
-----------
- 0 <= len(nums) <= 10^5, sorted non-decreasing.
- O(log n) time required.

Approach ladder
---------------
1. Brute force — linear scan for first and last, O(n).
2. Improved   — binary search to any hit, then expand left/right: O(log n + k)
   where k is the number of copies; degrades to O(n) when all equal.
3. Optimal    — two boundary searches: first = lower_bound(target),
   last = upper_bound(target) - 1. O(log n) regardless of duplicates.
   Invariant (half-open, lower_bound): every index < lo has nums[i] < x and
   every index >= hi has nums[i] >= x. When lo == hi, that is the boundary.

Follow-ups
----------
- Count occurrences in O(log n): upper_bound - lower_bound.
- Search insert position: lower_bound.
- Largest element <= x (floor): upper_bound(x) - 1; smallest >= x (ceiling): lower_bound(x).
- With a key function (Python 3.10+: bisect(..., key=...)).
"""
from __future__ import annotations

from bisect import bisect_left, bisect_right


def brute_force(nums: list[int], target: int) -> list[int]:
    first = last = -1
    for i, x in enumerate(nums):
        if x == target:
            if first == -1:
                first = i
            last = i
    return [first, last]


def expand_from_hit(nums: list[int], target: int) -> list[int]:
    """Rung 2: find any hit, then walk outwards. O(log n + k)."""
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            first = last = mid
            while first > 0 and nums[first - 1] == target:
                first -= 1
            while last < len(nums) - 1 and nums[last + 1] == target:
                last += 1
            return [first, last]
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return [-1, -1]


def lower_bound(nums: list[int], x: int) -> int:
    """First index i with nums[i] >= x (len(nums) if none). Same as bisect_left."""
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < x:
            lo = mid + 1          # mid is too small: boundary is right of mid
        else:
            hi = mid              # mid could be the boundary: keep it
    return lo


def upper_bound(nums: list[int], x: int) -> int:
    """First index i with nums[i] > x (len(nums) if none). Same as bisect_right."""
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def solve(nums: list[int], target: int) -> list[int]:
    first = lower_bound(nums, target)
    if first == len(nums) or nums[first] != target:
        return [-1, -1]
    return [first, upper_bound(nums, target) - 1]


def solve_bisect(nums: list[int], target: int) -> list[int]:
    first = bisect_left(nums, target)
    if first == len(nums) or nums[first] != target:
        return [-1, -1]
    return [first, bisect_right(nums, target) - 1]


def count_occurrences(nums: list[int], target: int) -> int:
    return upper_bound(nums, target) - lower_bound(nums, target)


def floor_ceiling(nums: list[int], x: int) -> tuple[int | None, int | None]:
    """Largest value <= x and smallest value >= x (None when absent)."""
    i = upper_bound(nums, x) - 1
    j = lower_bound(nums, x)
    return (nums[i] if i >= 0 else None, nums[j] if j < len(nums) else None)


def main() -> None:
    nums = [1, 2, 2, 2, 5, 7, 7, 9]
    print("nums:", nums)
    print(f"{'x':>3} {'lower':>5} {'bisect_left':>11} {'upper':>5} {'bisect_right':>12}")
    for x in (0, 1, 2, 4, 7, 9, 10):
        print(f"{x:>3} {lower_bound(nums, x):>5} {bisect_left(nums, x):>11} "
              f"{upper_bound(nums, x):>5} {bisect_right(nums, x):>12}")
    for t in (2, 7, 4, 1, 9):
        print(f"first/last of {t}: solve={solve(nums, t)} bisect={solve_bisect(nums, t)} "
              f"brute={brute_force(nums, t)} expand={expand_from_hit(nums, t)} "
              f"count={count_occurrences(nums, t)}")
    print("floor/ceiling of 6:", floor_ceiling(nums, 6))
    print("floor/ceiling of 0:", floor_ceiling(nums, 0))
    print("floor/ceiling of 10:", floor_ceiling(nums, 10))
    print("all equal [3,3,3,3]:", solve([3, 3, 3, 3], 3))
    print("empty:", solve([], 3))
    # bisect with key= (Python 3.10+): find the first record whose age >= 30
    people = [("ana", 22), ("bo", 30), ("cy", 30), ("di", 41)]
    i = bisect_left(people, 30, key=lambda p: p[1])
    print("first person aged >= 30:", people[i])


if __name__ == "__main__":
    main()
