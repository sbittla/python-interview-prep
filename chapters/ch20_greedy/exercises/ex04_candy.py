"""
Exercise 04 — Candy Distribution                                   [Tier: ★ Core]
Chapter 20 · Pattern: two-pass greedy (left and right constraints) · Target time: 25 min

Problem
-------
Children stand in a line with integer `ratings`. Give each child at least one candy, and any
child with a strictly higher rating than an immediate neighbour must get more candy than that
neighbour. Return the minimum total number of candies (and the distribution).

Examples
--------
>>> min_candies([1, 0, 2])
5
>>> min_candies([1, 2, 2])
4

Constraints
-----------
- 1 <= n <= 2 * 10^4, 0 <= ratings[i] <= 2 * 10^4.

Hints
-----
- Split the rule into two independent rules: one about left neighbours, one about right.
- Equal neighbours impose NO constraint.

Follow-ups
----------
- Circular arrangement: the two-pass trick needs care; start from a local minimum.
- O(1) extra space with slope counting.
"""
from __future__ import annotations


def brute_force(ratings: list[int]) -> int:
    raise NotImplementedError("TODO")


def distribute(ratings: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def min_candies(ratings: list[int]) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    ratings = [1, 3, 4, 5, 2, 1, 1, 2]
    n = len(ratings)
    left = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            left[i] = left[i - 1] + 1
    print("ratings     :", ratings)
    print("after pass 1:", left)
    print("after pass 2:", distribute(ratings))
    print("total       :", min_candies(ratings), "| brute force:", brute_force(ratings))
    print()
    for r in ([1, 0, 2], [1, 2, 2], [5], [3, 3, 3], [5, 4, 3, 2, 1], [1, 2, 3, 2, 1]):
        print(f"{str(r):<17} -> {distribute(r)} total {min_candies(r)}")
    # Tempting but wrong: one pass only
    r = [5, 4, 3, 2, 1]
    one_pass = [1] * len(r)
    for i in range(1, len(r)):
        if r[i] > r[i - 1]:
            one_pass[i] = one_pass[i - 1] + 1
    print("one pass only on", r, "->", one_pass, "(violates the rule: 5 > 4 but 1 == 1)")


if __name__ == "__main__":
    main()
