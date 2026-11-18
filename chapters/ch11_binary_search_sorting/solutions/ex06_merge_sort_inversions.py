"""
Exercise 06 — Merge Sort and Counting Inversions                   [Tier: ★ Core]
Chapter 11 · Pattern: divide and conquer / merge step · Target time: 25 min

Problem
-------
(a) Implement merge sort (top-down and bottom-up). It must be stable.
(b) An inversion is a pair of indices i < j with nums[i] > nums[j]. Count the
inversions of a list in O(n log n). (The count measures "how unsorted" a list
is; it is also the number of swaps bubble/insertion sort performs.)

Examples
--------
>>> solve([5, 2, 4, 6, 1, 3])
[1, 2, 3, 4, 5, 6]
>>> count_inversions([2, 4, 1, 3, 5])
3

Constraints
-----------
- 0 <= len(nums) <= 10^5.

Approach ladder
---------------
(b) 1. Brute force — check every pair, O(n^2).
    2. Improved   — insertion sort and count shifts: still O(n^2) worst case.
    3. Optimal    — piggy-back on merge sort. While merging sorted halves L and
       R, whenever R[j] is taken before the remaining L[i:], it forms an
       inversion with every one of those len(L) - i elements. O(n log n).

Follow-ups
----------
- Why is merge sort stable? On ties we take from the LEFT half first (<=).
- Sorting a linked list: merge sort needs O(1) extra space there (Ch. 13).
- External sort (data larger than memory): sort chunks, then k-way merge with a heap.
- Count of smaller numbers after self: same merge trick, tracking original indices.
"""
from __future__ import annotations


def merge(left: list, right: list) -> list:
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:        # '<=' keeps equal keys in original order (stable)
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])               # at most one of these is non-empty
    out.extend(right[j:])
    return out


def solve(nums: list) -> list:
    """Top-down merge sort. Returns a new list. O(n log n) time, O(n) space."""
    if len(nums) <= 1:
        return list(nums)
    mid = len(nums) // 2
    return merge(solve(nums[:mid]), solve(nums[mid:]))


def merge_sort_bottom_up(nums: list) -> list:
    """Iterative: merge runs of width 1, 2, 4, ... No recursion depth issues."""
    a = list(nums)
    width = 1
    while width < len(a):
        for lo in range(0, len(a), 2 * width):
            mid = min(lo + width, len(a))
            hi = min(lo + 2 * width, len(a))
            a[lo:hi] = merge(a[lo:mid], a[mid:hi])
        width *= 2
    return a


def merge_sort_trace(nums: list, depth: int = 0, lines: list[str] | None = None) -> list:
    """Same algorithm, recording each split and merge for the book's diagram."""
    if lines is None:
        lines = []
    pad = "  " * depth
    if len(nums) <= 1:
        return list(nums)
    mid = len(nums) // 2
    lines.append(f"{pad}split {nums} -> {nums[:mid]} | {nums[mid:]}")
    merged = merge(merge_sort_trace(nums[:mid], depth + 1, lines),
                   merge_sort_trace(nums[mid:], depth + 1, lines))
    lines.append(f"{pad}merge -> {merged}")
    return merged


def brute_force_inversions(nums: list) -> int:
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i + 1, n) if nums[i] > nums[j])


def count_inversions(nums: list) -> int:
    def sort_count(a: list) -> tuple[list, int]:
        if len(a) <= 1:
            return list(a), 0
        mid = len(a) // 2
        left, inv_l = sort_count(a[:mid])
        right, inv_r = sort_count(a[mid:])
        out, i, j, inv = [], 0, 0, inv_l + inv_r
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                inv += len(left) - i     # right[j] jumps over every remaining left item
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out, inv

    return sort_count(nums)[1]


def main() -> None:
    data = [38, 27, 43, 3, 9, 82, 10]
    lines: list[str] = []
    result = merge_sort_trace(data, lines=lines)
    print("\n".join(lines))
    print("sorted:", result)
    print("bottom-up:", merge_sort_bottom_up(data))
    print("empty / one:", solve([]), solve([7]))
    # stability: sort records by grade only; equal grades keep input order
    records = [("dee", 2), ("ann", 1), ("bob", 2), ("cat", 1)]
    keyed = [(g, i, name) for i, (name, g) in enumerate(records)]
    merged = [name for g, i, name in solve(keyed)]
    print("stable order by grade:", merged)
    for arr in ([2, 4, 1, 3, 5], [5, 4, 3, 2, 1], [1, 2, 3], [1, 1, 1], []):
        print(f"inversions {arr}: merge={count_inversions(arr)} brute={brute_force_inversions(arr)}")


if __name__ == "__main__":
    main()
