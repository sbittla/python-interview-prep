"""
Exercise 01 — Subsets (power set)                  [Tier: ★ Core]
Chapter 18 · Pattern: backtracking (start index) · Target time: 10 min

Problem
-------
Given a list of distinct integers, return every subset of it (the power set). Inside a subset the
elements keep their input order. The order of the subsets in the result does not matter.

Examples
--------
>>> sorted(solve([1, 2, 3]))
[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
>>> solve([])
[[]]

Constraints
-----------
- 0 <= len(nums) <= 12
- All values are distinct.

Hints
-----
- Each element is either in or out, so there are 2**n subsets.
- Backtracking with a start index: record the current path, then try extending it with every
  later index.
- Record a copy (path[:]) — otherwise every stored subset aliases the same list.

Approach ladder
---------------
1. Brute force — count a bitmask from 0 to 2**n - 1; bit i set means nums[i] is in.
   O(n * 2^n) time, O(n * 2^n) output.
2. Optimal    — backtracking with a start index; every node of the recursion tree is a subset.
   Same O(n * 2^n) time (the output is that large), O(n) extra stack/path space.
   Why move up: the template extends to duplicates, size limits and pruning; the bitmask does not.

Follow-ups
----------
- The input contains duplicates (Exercise 02).
- Only subsets of size k (Exercise 05).
- Yield subsets lazily with a generator instead of building a list.
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> list[list[int]]:
    n = len(nums)
    return [[nums[i] for i in range(n) if mask >> i & 1] for mask in range(1 << n)]


def solve(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int) -> None:
        result.append(path[:])             # every node is a valid subset
        for i in range(start, len(nums)):
            path.append(nums[i])           # choose
            backtrack(i + 1)               # explore (only later indices)
            path.pop()                     # unchoose

    backtrack(0)
    return result


def trace(nums: list[int]) -> list[str]:
    """Return the recursion tree of solve() as indented lines (one line per call)."""
    lines: list[str] = []
    path: list[int] = []

    def backtrack(start: int, depth: int) -> None:
        lines.append("    " * depth + str(path))
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, depth + 1)
            path.pop()

    backtrack(0, 0)
    return lines


def main() -> None:
    print("solve([1, 2, 3])       =", solve([1, 2, 3]))
    print("brute_force([1, 2, 3]) =", brute_force([1, 2, 3]))
    print("same set of subsets    :", sorted(solve([1, 2, 3])) == sorted(brute_force([1, 2, 3])))
    print("solve([])              =", solve([]))
    print("count for n=10         =", len(solve(list(range(10)))))
    print("recursion tree for [1, 2, 3] (each line is one call = one subset):")
    for line in trace([1, 2, 3]):
        print("  " + line)


if __name__ == "__main__":
    main()
