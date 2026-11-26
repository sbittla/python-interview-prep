"""
Exercise 14 — Practice Set: Peak, Integer Square Root, Median of Two Sorted Lists
                                                                   [Tier: ◆ Extended]
Chapter 11 · Pattern: binary search on an implicit monotonic property · Target time: 40 min

Problem
-------
(a) Peak element: in a list where neighbours differ, return the index of any
element strictly greater than its neighbours (treat out-of-bounds as -infinity).
(b) Integer square root: return floor(sqrt(x)) for x >= 0 without math.sqrt.
(c) Find the duplicate: a list of n + 1 integers drawn from 1..n has exactly one
value repeated (possibly several times). Find it without modifying the list
and with O(1) extra space.
(d) Median of two sorted lists in O(log(min(m, n))). This is `solve`.

Examples
--------
>>> find_peak([1, 2, 3, 1])
2
>>> int_sqrt(8)
2
>>> find_duplicate([1, 3, 4, 2, 2])
2
>>> solve([1, 3], [2])
2.0
>>> solve([1, 2], [3, 4])
2.5

Constraints
-----------
- (d) 0 <= m, n and m + n >= 1.

Approach ladder
---------------
(a) Linear scan O(n) -> binary search on the slope: if nums[mid] < nums[mid+1]
    a peak exists on the right (we are climbing), else on the left. O(log n).
(b) Count up O(sqrt x) -> first_true(y*y > x) - 1. O(log x).
(c) Sort O(n log n) or set O(n) space -> binary search on VALUE v: count of
    elements <= v exceeds v exactly when the duplicate is <= v. O(n log n), O(1).
(d) 1. Merge both lists, take the middle: O(m + n).
    2. Merge only up to the middle with two pointers: O(m + n), O(1) space.
    3. Binary search the cut in the shorter list. Cut A at i and B at
       j = half - i; the cut is right when A[i-1] <= B[j] and B[j-1] <= A[i].
       O(log min(m, n)).

Wrong-but-tempting
------------------
- (a) Comparing nums[mid] with nums[mid - 1] and moving the wrong way, or
  reading nums[mid + 1] with a closed loop `while lo <= hi` (index error at
  the end).
- (b) Searching [0, x // 2]: wrong for x = 1 (floor(sqrt(1)) = 1 > 0).
- (d) Binary searching the LONGER list: j = half - i can go negative.

Follow-ups
----------
- k-th smallest of two sorted lists: same partition idea, or discard k/2 per step.
- Peak in a 2D grid: binary search on columns + column maximum, O(m log n).
"""
from __future__ import annotations

from bisect import bisect_right


def find_peak(nums: list[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1              # climbing: a peak lies to the right
        else:
            hi = mid                  # descending: mid or something left is a peak
    return lo


def int_sqrt(x: int) -> int:
    lo, hi = 0, x + 1                 # find the first y with y*y > x in [0, x+1]
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid > x:
            hi = mid
        else:
            lo = mid + 1
    return lo - 1


def find_duplicate(nums: list[int]) -> int:
    lo, hi = 1, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(1 for x in nums if x <= mid) > mid:   # pigeonhole: duplicate <= mid
            hi = mid
        else:
            lo = mid + 1
    return lo


def brute_force(a: list[int], b: list[int]) -> float:
    merged = sorted(a + b)
    n = len(merged)
    if n % 2:
        return float(merged[n // 2])
    return (merged[n // 2 - 1] + merged[n // 2]) / 2


def median_two_pointers(a: list[int], b: list[int]) -> float:
    """Rung 2: walk a merge only up to the middle. O(m + n) time, O(1) space."""
    n = len(a) + len(b)
    i = j = 0
    prev = cur = 0
    for _ in range(n // 2 + 1):           # advance to the element at index n // 2
        prev = cur
        if j >= len(b) or (i < len(a) and a[i] <= b[j]):
            cur = a[i]
            i += 1
        else:
            cur = b[j]
            j += 1
    return float(cur) if n % 2 else (prev + cur) / 2


def median_by_counting(a: list[int], b: list[int]) -> float:
    """Cross-check: k-th smallest by binary search over candidate VALUES,
    counting with bisect_right. O((m + n) log(m + n)) because of the set/sort."""
    n = len(a) + len(b)

    def kth(k: int) -> int:           # k-th smallest, 1-based, by binary search on candidate values
        cands = sorted(set(a) | set(b))
        lo, hi = 0, len(cands) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if bisect_right(a, cands[mid]) + bisect_right(b, cands[mid]) >= k:
                hi = mid
            else:
                lo = mid + 1
        return cands[lo]

    if n % 2:
        return float(kth(n // 2 + 1))
    return (kth(n // 2) + kth(n // 2 + 1)) / 2


def solve(a: list[int], b: list[int]) -> float:
    if len(a) > len(b):
        a, b = b, a                   # binary search the shorter list
    m, n = len(a), len(b)
    half = (m + n + 1) // 2           # size of the left part (extra element goes left)
    lo, hi = 0, m
    inf = float("inf")
    while lo <= hi:
        i = (lo + hi) // 2            # elements taken from a
        j = half - i                  # elements taken from b
        a_left = a[i - 1] if i > 0 else -inf
        a_right = a[i] if i < m else inf
        b_left = b[j - 1] if j > 0 else -inf
        b_right = b[j] if j < n else inf
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2:
                return float(max(a_left, b_left))
            return (max(a_left, b_left) + min(a_right, b_right)) / 2
        if a_left > b_right:
            hi = i - 1                # took too many from a
        else:
            lo = i + 1                # took too few from a
    raise ValueError("inputs must be sorted")


def main() -> None:
    for nums in ([1, 2, 3, 1], [1, 2, 1, 3, 5, 6, 4], [5], [3, 2, 1], [1, 2, 3]):
        print(f"peak index of {nums}: {find_peak(nums)}")
    print("int_sqrt:", {x: int_sqrt(x) for x in (0, 1, 2, 3, 4, 8, 9, 15, 16, 10**12)})
    for nums in ([1, 3, 4, 2, 2], [3, 1, 3, 4, 2], [2, 2, 2, 2, 2]):
        print(f"duplicate in {nums}: {find_duplicate(nums)}")
    pairs = [([1, 3], [2]), ([1, 2], [3, 4]), ([], [1]), ([2], []), ([1, 2, 3], [4, 5, 6, 7, 8]),
             ([0, 0], [0, 0]), ([-5, 3, 6, 12, 15], [-12, -10, -6, -3, 4, 10])]
    for a, b in pairs:
        print(f"median {a} + {b}: partition={solve(a, b)} two-ptr={median_two_pointers(a, b)} "
              f"counting={median_by_counting(a, b)} merge={brute_force(a, b)}")


if __name__ == "__main__":
    main()
