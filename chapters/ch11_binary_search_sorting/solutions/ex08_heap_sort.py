"""
Exercise 08 — Heap Sort                                            [Tier: ★ Core]
Chapter 11 · Pattern: binary heap in an array · Target time: 20 min

Problem
-------
Sort a list in place in O(n log n) worst-case time using O(1) extra space by
building a max-heap inside the list and repeatedly moving the maximum to the end.
Write sift_down and build_max_heap yourself; then show the heapq shortcut.

Examples
--------
>>> solve([4, 10, 3, 5, 1])
[1, 3, 4, 5, 10]

Constraints
-----------
- 0 <= len(nums) <= 10^5.

Approach ladder
---------------
1. Selection sort — repeatedly scan for the maximum: O(n^2).
2. Improved   — keep the unsorted part in a heap so "find max" is O(log n):
   with heapq (a min-heap) in a separate list: O(n log n) time, O(n) space.
3. Optimal    — in-place max-heap: build with bottom-up sift_down in O(n),
   then n-1 times swap root with the last heap slot and sift_down.
   O(n log n) worst case, O(1) extra space. Not stable.

Follow-ups
----------
- Why is building a heap O(n), not O(n log n)? Most nodes are near the bottom
  and sift down only a little: sum over heights h of (n / 2^(h+1)) * h = O(n).
- Children of index i are 2i+1 and 2i+2; parent is (i-1)//2.
- In practice quick sort / Timsort beat heap sort (cache locality), but heap
  sort's worst-case guarantee is why introsort falls back to it.
"""
from __future__ import annotations

import heapq


def sift_down(a: list, i: int, size: int) -> None:
    """Move a[i] down until both children are <= it (max-heap), within a[:size]."""
    while True:
        largest = i
        left, right = 2 * i + 1, 2 * i + 2
        if left < size and a[left] > a[largest]:
            largest = left
        if right < size and a[right] > a[largest]:
            largest = right
        if largest == i:
            return
        a[i], a[largest] = a[largest], a[i]
        i = largest


def build_max_heap(a: list) -> None:
    for i in range(len(a) // 2 - 1, -1, -1):   # last internal node down to the root
        sift_down(a, i, len(a))


def heap_sort_in_place(a: list, trace: list[str] | None = None) -> None:
    build_max_heap(a)
    if trace is not None:
        trace.append(f"max-heap built : {a}")
    for end in range(len(a) - 1, 0, -1):
        a[0], a[end] = a[end], a[0]           # move current max to its final slot
        sift_down(a, 0, end)                  # restore heap on the shrunken prefix
        if trace is not None:
            trace.append(f"heap={a[:end]} | sorted={a[end:]}")


def heap_sort_heapq(nums: list) -> list:
    h = list(nums)
    heapq.heapify(h)                          # O(n) min-heap
    return [heapq.heappop(h) for _ in range(len(h))]


def selection_sort_max(nums: list) -> list:
    a = list(nums)
    for end in range(len(a) - 1, 0, -1):
        m = max(range(end + 1), key=a.__getitem__)
        a[m], a[end] = a[end], a[m]
    return a


def is_max_heap(a: list) -> bool:
    return all(a[(i - 1) // 2] >= a[i] for i in range(1, len(a)))


def solve(nums: list) -> list:
    a = list(nums)
    heap_sort_in_place(a)
    return a


def main() -> None:
    data = [4, 10, 3, 5, 1]
    a = list(data)
    trace: list[str] = []
    heap_sort_in_place(a, trace)
    print("input:", data)
    print("\n".join(trace))
    print("result:", a)
    b = [3, 9, 2, 1, 4, 5]
    build_max_heap(b)
    print("build_max_heap([3, 9, 2, 1, 4, 5]):", b, "valid heap:", is_max_heap(b))
    sample = [9, -2, 7, 7, 0, 15, -8, 3]
    print("in-place :", solve(sample))
    print("heapq    :", heap_sort_heapq(sample))
    print("selection:", selection_sort_max(sample))
    print("edge cases:", solve([]), solve([1]), solve([2, 1]), solve([5, 5, 5]))


if __name__ == "__main__":
    main()
