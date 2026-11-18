"""
Exercise 03 — Permutations                         [Tier: ★ Core]
Chapter 18 · Pattern: backtracking (used[] array) · Target time: 10 min

Problem
-------
Given a list of distinct integers, return all of its orderings.

Examples
--------
>>> solve([1, 2, 3])
[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]

Constraints
-----------
- 0 <= len(nums) <= 8
- All values are distinct.

Hints
-----
- Unlike subsets, every position may hold any unused element, so loop from index 0 each time.
- Track which indices are already in the path with a boolean list.
- Record a result only at the leaves (when the path has n elements).

Approach ladder
---------------
1. Brute force — itertools.permutations (fine in production; interviewers want the recursion).
2. Optimal    — backtracking with a used[] array: n! leaves, O(n * n!) time, O(n) extra space.
   An in-place swap variant avoids the used[] array but does not produce lexicographic order.

Follow-ups
----------
- Duplicates in the input (Exercise 04).
- Next permutation in lexicographic order, in place, O(n).
- k-th permutation without generating the others (factorial number system).
"""
from __future__ import annotations

from itertools import permutations


def brute_force(nums: list[int]) -> list[list[int]]:
    return [list(p) for p in permutations(nums)]


def solve(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    path: list[int] = []
    used = [False] * len(nums)

    def backtrack() -> None:
        if len(path) == len(nums):          # leaf: a full permutation
            result.append(path[:])
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True                  # choose
            path.append(x)
            backtrack()                     # explore
            path.pop()                      # unchoose
            used[i] = False

    backtrack()
    return result


def solve_swap(nums: list[int]) -> list[list[int]]:
    """In-place swap variant: position `first` takes each remaining element in turn."""
    nums = nums[:]
    result: list[list[int]] = []

    def backtrack(first: int) -> None:
        if first == len(nums):
            result.append(nums[:])
            return
        for i in range(first, len(nums)):
            nums[first], nums[i] = nums[i], nums[first]
            backtrack(first + 1)
            nums[first], nums[i] = nums[i], nums[first]

    backtrack(0)
    return result


def trace(nums: list[int]) -> list[str]:
    """Recursion tree of solve() as indented lines."""
    lines: list[str] = []
    path: list[int] = []
    used = [False] * len(nums)

    def backtrack(depth: int) -> None:
        leaf = len(path) == len(nums)
        lines.append("    " * depth + str(path) + ("  <- leaf" if leaf else ""))
        if leaf:
            return
        for i, x in enumerate(nums):
            if not used[i]:
                used[i] = True
                path.append(x)
                backtrack(depth + 1)
                path.pop()
                used[i] = False

    backtrack(0)
    return lines


def main() -> None:
    print("solve([1, 2, 3])      =", solve([1, 2, 3]))
    print("solve_swap([1, 2, 3]) =", solve_swap([1, 2, 3]))
    print("matches itertools     :", solve([1, 2, 3]) == brute_force([1, 2, 3]))
    print("solve([])             =", solve([]))
    print("count for n=6         =", len(solve(list(range(6)))))
    print("recursion tree for [1, 2, 3]:")
    for line in trace([1, 2, 3]):
        print("  " + line)


if __name__ == "__main__":
    main()
