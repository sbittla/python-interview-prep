"""
Exercise 01 — Move Zeroes to the End                    [Tier: ★ Core]
Chapter 09 · Pattern: in-place write pointer · Target time: 10 min

Problem
-------
Given a list of integers, move every 0 to the end of the list while keeping the
relative order of the non-zero values. Do it in place (O(1) extra space). For
convenience, return the same list object after modifying it.

Examples
--------
>>> solve([0, 1, 0, 3, 12])
[1, 3, 12, 0, 0]
>>> solve([0])
[0]

Constraints
-----------
- 0 <= len(nums) <= 10**5
- Values are any integers; only exact 0 is moved.

Hints
-----
- The output order of the non-zeros is the input order. What is the earliest slot each one can land in?
- Can a single left-to-right scan know where the next non-zero belongs?
- Implement brute_force (extra list) and bubble first; compare their costs.

Follow-ups
----------
- Minimise the number of writes.
- Move all values equal to a given target, or all negatives, to the end.
- Stable partition by any predicate (this is the same template).
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> list[int]:
    """O(n) extra space: rebuild then copy back."""
    raise NotImplementedError("TODO")


def bubble(nums: list[int]) -> list[int]:
    """In place but O(n^2): repeatedly swap a zero with its right neighbour."""
    raise NotImplementedError("TODO")


def solve(nums: list[int]) -> list[int]:
    """Write-pointer swap: O(n) time, O(1) space, stable for non-zeros."""
    raise NotImplementedError("TODO")


def main() -> None:
    cases = [[0, 1, 0, 3, 12], [0], [], [1, 2, 3], [0, 0, 1], [4, 0, -2, 0, 0, 7]]
    for case in cases:
        a, b, c = list(case), list(case), list(case)
        print(f"{case!s:<22} -> {solve(a)}  (brute={brute_force(b) == a}, bubble={bubble(c) == a})")


if __name__ == "__main__":
    main()
