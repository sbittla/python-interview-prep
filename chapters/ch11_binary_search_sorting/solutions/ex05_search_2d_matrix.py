"""
Exercise 05 — Binary Search on 2D Matrices                         [Tier: ★ Core]
Chapter 11 · Pattern: index mapping / staircase / value-space search · Target time: 20 min

Problem
-------
(a) Each row of an m x n matrix is sorted, and the first value of each row is
greater than the last value of the previous row. Report whether target exists.
(b) Weaker guarantee: every row is sorted left-to-right and every column is
sorted top-to-bottom. Report whether target exists.
(c) ◆ With guarantee (b), return the k-th smallest value (1-based).

Examples
--------
>>> solve([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3)
True
>>> search_staircase([[1, 4, 7], [2, 5, 8], [3, 6, 9]], 10)
False
>>> kth_smallest([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8)
13

Constraints
-----------
- 0 <= m, n <= 300.

Approach ladder
---------------
(a) 1. Scan everything, O(mn). 2. Binary search the row, then the column,
    O(log m + log n). 3. Treat the matrix as one sorted list of length m*n:
    index i maps to (i // n, i % n). O(log(mn)), one loop, fewest bugs.
(b) 1. Scan, O(mn). 2. Binary search each row, O(m log n).
    3. Staircase from the top-right corner: if value > target move left (whole
    column below is bigger), if smaller move down. O(m + n).
(c) 1. Flatten and sort, O(mn log mn). 2. Heap of row heads, O(k log m).
    3. Binary search on the VALUE: count entries <= x with a staircase walk
    (O(m + n)) and find the first x whose count >= k. O((m+n) log(max-min)).

Follow-ups
----------
- Why top-right and not top-left? From top-left both moves increase the value,
  so you cannot decide; top-right (or bottom-left) gives one "bigger" and one
  "smaller" direction.
- Count negatives in a row/column-sorted matrix: same staircase, O(m + n).
"""
from __future__ import annotations

import heapq


def brute_force(matrix: list[list[int]], target: int) -> bool:
    return any(target in row for row in matrix)


def solve(matrix: list[list[int]], target: int) -> bool:
    """Fully sorted (row-major) matrix: virtual 1D binary search."""
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        val = matrix[mid // n][mid % n]
        if val == target:
            return True
        if val < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False


def search_staircase(matrix: list[list[int]], target: int) -> bool:
    """Rows and columns sorted: walk from the top-right corner."""
    if not matrix or not matrix[0]:
        return False
    r, c = 0, len(matrix[0]) - 1
    while r < len(matrix) and c >= 0:
        val = matrix[r][c]
        if val == target:
            return True
        if val > target:
            c -= 1                    # everything below in this column is even larger
        else:
            r += 1                    # everything left in this row is even smaller
    return False


def count_less_equal(matrix: list[list[int]], x: int) -> int:
    n = len(matrix)
    r, c, count = n - 1, 0, 0          # start bottom-left
    while r >= 0 and c < len(matrix[0]):
        if matrix[r][c] <= x:
            count += r + 1             # whole column segment above is <= x
            c += 1
        else:
            r -= 1
    return count


def kth_smallest_heap(matrix: list[list[int]], k: int) -> int:
    heap = [(row[0], i, 0) for i, row in enumerate(matrix)]
    heapq.heapify(heap)
    for _ in range(k - 1):
        val, i, j = heapq.heappop(heap)
        if j + 1 < len(matrix[i]):
            heapq.heappush(heap, (matrix[i][j + 1], i, j + 1))
    return heap[0][0]


def kth_smallest(matrix: list[list[int]], k: int) -> int:
    lo, hi = matrix[0][0], matrix[-1][-1]
    while lo < hi:
        mid = (lo + hi) // 2
        if count_less_equal(matrix, mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo                          # lo is always a value present in the matrix


def main() -> None:
    a = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
    for t in (3, 13, 60, 1, 0, 61):
        print(f"(a) target={t:>2}: virtual-1D={solve(a, t)} brute={brute_force(a, t)}")
    print("(a) index 6 maps to row/col:", divmod(6, 4), "->", a[6 // 4][6 % 4])
    b = [[1, 4, 7, 11, 15], [2, 5, 8, 12, 19], [3, 6, 9, 16, 22],
         [10, 13, 14, 17, 24], [18, 21, 23, 26, 30]]
    for t in (5, 20, 30, 18, 0):
        print(f"(b) target={t:>2}: staircase={search_staircase(b, t)} brute={brute_force(b, t)}")
    c = [[1, 5, 9], [10, 11, 13], [12, 13, 15]]
    print("(c) all k:", [kth_smallest(c, k) for k in range(1, 10)])
    print("(c) heap agrees:", [kth_smallest_heap(c, k) for k in range(1, 10)])
    print("empty matrix:", solve([], 1), solve([[]], 1), search_staircase([[]], 1))


if __name__ == "__main__":
    main()
