"""
Exercise 08 — Greedy vs DP: Coin Change and Knapsack                [Tier: ★ Core]
Chapter 20 · Pattern: recognising when greedy fails · Target time: 30 min

Problem
-------
1. `greedy_coins(coins, amount)` — repeatedly take the largest coin that fits; return the
   number of coins used, or -1 if it gets stuck.
2. `min_coins(coins, amount)` — the true minimum number of coins (unlimited supply) or -1.
3. `find_counterexample(coins, limit)` — the smallest amount <= limit where greedy is not
   optimal (or None). This tells you whether a coin system is "canonical".
4. `fractional_knapsack(items, cap)` and `knapsack_01(items, cap)` — items are
   (value, weight). Fractional allows taking part of an item; 0/1 does not.

Examples
--------
>>> greedy_coins([1, 3, 4], 6), min_coins([1, 3, 4], 6)
(3, 2)
>>> find_counterexample([1, 5, 10, 25], 200) is None
True

Constraints
-----------
- 1 <= len(coins) <= 12, 1 <= coins[i] <= 10^4, 0 <= amount <= 10^4.

Hints
-----
- To prove greedy wrong, you only need one counterexample; brute force small amounts.
- In 0/1 knapsack, a high-ratio item can waste capacity that two others would have filled.

Follow-ups
----------
- Count the number of ways to make the amount (combinations, order does not matter).
- Kozen-Zaks: if a coin system fails, a counterexample exists below c[-1] + c[-2].
"""
from __future__ import annotations


def greedy_coins(coins: list[int], amount: int) -> int:
    raise NotImplementedError("TODO")


def min_coins(coins: list[int], amount: int) -> int:
    raise NotImplementedError("TODO")


def find_counterexample(coins: list[int], limit: int) -> int | None:
    raise NotImplementedError("TODO")


def fractional_knapsack(items: list[tuple[int, int]], cap: int) -> float:
    raise NotImplementedError("TODO")


def greedy_01_by_ratio(items: list[tuple[int, int]], cap: int) -> int:
    raise NotImplementedError("TODO")


def knapsack_01(items: list[tuple[int, int]], cap: int) -> int:
    raise NotImplementedError("TODO")


def main() -> None:
    print("coin systems (amount -> greedy / optimal):")
    for coins in ([1, 5, 10, 25], [1, 3, 4], [1, 7, 10], [1, 15, 25], [1, 2, 5, 10, 20, 50, 100, 200], [3, 5]):
        cx = find_counterexample(coins, 100)
        if cx is None:
            print(f"  {coins}: canonical up to 100")
        else:
            print(f"  {coins}: first failure at {cx}: greedy {greedy_coins(coins, cx)}, "
                  f"optimal {min_coins(coins, cx)}")
    print("  [3, 5] amount 7 -> greedy", greedy_coins([3, 5], 7), "| optimal", min_coins([3, 5], 7))
    print("  [3, 5] amount 9 -> greedy", greedy_coins([3, 5], 9), "| optimal", min_coins([3, 5], 9))
    print()
    items = [(60, 10), (100, 20), (120, 30)]      # (value, weight)
    cap = 50
    print("items (value, weight):", items, "capacity", cap)
    print("  fractional greedy        :", fractional_knapsack(items, cap))
    print("  0/1 greedy by ratio      :", greedy_01_by_ratio(items, cap))
    print("  0/1 dynamic programming  :", knapsack_01(items, cap))


if __name__ == "__main__":
    main()
