"""
Exercise 04 — 0/1 Knapsack and Coin Change (min coins, number of ways) [Tier: ★ Core]
Chapter 19 · Pattern: knapsack over capacity · Target time: 40 min

Problem
-------
Items are (weight, value) pairs with weight >= 1; coins are distinct positive values.
1. `knapsack(items, cap)` — each item used at most once (0/1); maximise total value
   with total weight <= cap. `knapsack_table` also returns the chosen item indices.
2. `knapsack_unbounded(items, cap)` — each item may be used any number of times.
3. `min_coins(coins, amount)` — fewest coins (unlimited supply) summing to amount,
   or -1 if impossible. `greedy_coins` is the tempting largest-coin-first answer.
4. `count_combinations(coins, amount)` — number of multisets of coins summing to
   amount (1+2 and 2+1 are the SAME way).
5. `count_permutations(coins, amount)` — number of ordered sequences (1+2 and 2+1
   are DIFFERENT ways).

Examples
--------
>>> knapsack([(1, 1), (3, 4), (4, 5), (5, 7)], 7)
9
>>> knapsack_unbounded([(1, 1), (3, 4), (4, 5), (5, 7)], 7)
9
>>> min_coins([1, 3, 4], 6), greedy_coins([1, 3, 4], 6)
(2, 3)
>>> count_combinations([1, 2, 5], 5), count_permutations([1, 2, 5], 5)
(4, 9)

Constraints
-----------
- 0 <= len(items) <= 100, 0 <= cap <= 10^4; 1 <= len(coins) <= 50, 0 <= amount <= 10^4.
- amount 0 has exactly one way (no coins) and needs 0 coins.

Hints
-----
- The memoised rung recurses ~amount deep and hits the ~1000 limit (section 7.21) well inside
  the constraints; this is why the final answer is a table.
- Draw the 0/1 table: row i depends only on row i-1. Which cells of row i-1 are still
  intact if you overwrite right to left?
- min_coins: initialise with a sentinel larger than any answer (amount + 1), not 0.
- Counting: ask "is 1+2 the same as 2+1 here?" before choosing the loop order.

Follow-ups
----------
- Partition equal subset sum = 0/1 knapsack with boolean cells (target sum // 2).
- Target sum with +/- signs reduces to counting subsets with a given sum.
- Bounded knapsack (item i at most k_i times): binary-split each item into 1, 2, 4, ...
"""
from __future__ import annotations

from functools import cache

Item = tuple[int, int]                          # (weight, value)


# ---------------------------------------------------------------- 0/1 knapsack
def knapsack_brute(items: list[Item], cap: int) -> int:
    raise NotImplementedError("TODO")


def knapsack_memo(items: list[Item], cap: int) -> int:
    raise NotImplementedError("TODO")


def knapsack_table(items: list[Item], cap: int) -> tuple[int, list[int]]:
    raise NotImplementedError("TODO")


def knapsack(items: list[Item], cap: int) -> int:
    raise NotImplementedError("TODO")


def knapsack_unbounded_brute(items: list[Item], cap: int) -> int:
    raise NotImplementedError("TODO")


def knapsack_unbounded(items: list[Item], cap: int) -> int:
    raise NotImplementedError("TODO")


# ---------------------------------------------------------------- coin change
def greedy_coins(coins: list[int], amount: int) -> int:
    """Wrong-but-tempting: largest coin first. Optimal only for canonical systems."""
    raise NotImplementedError("TODO")


def min_coins_brute(coins: list[int], amount: int) -> int:
    raise NotImplementedError("TODO")


def min_coins_memo(coins: list[int], amount: int) -> int:
    raise NotImplementedError("TODO")


def min_coins(coins: list[int], amount: int) -> int:
    raise NotImplementedError("TODO")


# ---------------------------------------------------------------- counting ways
def count_combinations_brute(coins: list[int], amount: int) -> int:
    raise NotImplementedError("TODO")


def count_combinations_memo(coins: list[int], amount: int) -> int:
    raise NotImplementedError("TODO")


def count_combinations(coins: list[int], amount: int) -> int:
    raise NotImplementedError("TODO")


def count_permutations_brute(coins: list[int], amount: int) -> int:
    raise NotImplementedError("TODO")


def count_permutations(coins: list[int], amount: int) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    items = [(1, 1), (3, 4), (4, 5), (5, 7)]
    print("0/1 knapsack cap 7:", knapsack(items, 7), "table + chosen:", knapsack_table(items, 7),
          "brute/memo:", knapsack_brute(items, 7), knapsack_memo(items, 7))
    print("unbounded cap 7:", knapsack_unbounded(items, 7),
          "brute:", knapsack_unbounded_brute(items, 7))
    print("single item (2, 3), cap 6:  0/1 =", knapsack([(2, 3)], 6),
          " unbounded (forward loop) =", knapsack_unbounded([(2, 3)], 6))
    for coins, amount in (([1, 3, 4], 6), ([1, 5, 10, 25], 30), ([2], 3), ([7, 3], 0)):
        print(f"coins {coins} amount {amount}: min = {min_coins(coins, amount)}, "
              f"greedy = {greedy_coins(coins, amount)}, "
              f"brute/memo = {min_coins_brute(coins, amount)}/{min_coins_memo(coins, amount)}")
    print("min_coins([1, 5, 10, 25], 9999):", min_coins([1, 5, 10, 25], 9999))
    for coins, amount in (([1, 2, 5], 5), ([2, 3], 7), ([3], 2), ([1, 2], 4)):
        print(f"ways to make {amount} from {coins}: combinations = "
              f"{count_combinations(coins, amount)}, permutations = "
              f"{count_permutations(coins, amount)}")


if __name__ == "__main__":
    main()
