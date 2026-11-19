"""
Exercise 05 — Find the Duplicate (Floyd) and Happy Numbers  [Tier: ◆ Extended]
Chapter 10 · Pattern: fast and slow pointers on a function graph · Target time: 25 min

Problem
-------
(a) find_duplicate: nums has n + 1 integers, each in 1..n, so by pigeonhole at
    least one value repeats; exactly one value repeats (possibly many times).
    Return it without modifying nums and with O(1) extra space.
(b) is_happy: starting from a positive integer, repeatedly replace it by the
    sum of the squares of its digits. Return True if the sequence reaches 1.

Examples
--------
>>> solve([1, 3, 4, 2, 2])
2
>>> solve([3, 1, 3, 4, 2])
3
>>> is_happy(19), is_happy(2)
(True, False)

Constraints
-----------
- (a) 1 <= n <= 10**5. (b) 1 <= x <= 2**31 - 1.

Hints
-----
- Treat i -> nums[i] as a linked structure starting at index 0.
- A value with two incoming arrows is the entrance of a cycle: Floyd's two phases.
- is_happy: the digit-square sequence is eventually periodic; detect the loop.

Wrong-but-tempting
------------------
- sum(nums) - n*(n+1)//2: works only when the duplicate appears exactly twice.
- Returning the meeting point of phase 1: it is *on* the cycle, not
  necessarily its entrance.

Follow-ups
----------
- Why not mark visited by negating nums[abs(x)]? It is O(1) space but
  modifies the input, which the problem forbids.
"""
from __future__ import annotations


def brute_force(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def seen_set(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def count_binary_search(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def wrong_sum_formula(nums: list[int]) -> int:
    """Wrong-but-tempting: assumes the duplicate appears exactly twice."""
    n = len(nums) - 1
    return sum(nums) - n * (n + 1) // 2


def solve(nums: list[int]) -> int:
    raise NotImplementedError("TODO")


def _digit_square_sum(x: int) -> int:
    total = 0
    while x:
        x, d = divmod(x, 10)
        total += d * d
    return total


def is_happy_set(x: int) -> bool:
    raise NotImplementedError("TODO")


def is_happy(x: int) -> bool:
    raise NotImplementedError("TODO")


def main() -> None:
    for nums in ([1, 3, 4, 2, 2], [3, 1, 3, 4, 2], [1, 1], [2, 2, 2, 2, 2], [4, 3, 1, 4, 2, 4]):
        print(f"nums={nums!s:<20} -> {solve(nums)}  brute={brute_force(nums)}"
              f"  binsearch={count_binary_search(nums)}  sum-formula(wrong)={wrong_sum_formula(nums)}")
    happy = [x for x in range(1, 50) if is_happy(x)]
    print("happy numbers below 50:", happy)
    print("Floyd agrees with set on 1..2000:",
          all(is_happy(x) == is_happy_set(x) for x in range(1, 2001)))


if __name__ == "__main__":
    main()
