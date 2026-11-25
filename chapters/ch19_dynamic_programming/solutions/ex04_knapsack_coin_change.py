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

Approach ladder
---------------
0/1 knapsack recipe — state: best(i, c) = most value from items[:i] with capacity c;
transition: best(i, c) = max(best(i-1, c), v + best(i-1, c-w) if w <= c);
base: best(0, c) = 0; order: i ascending (any c order with a full table); answer:
best(n, cap).
1. Plain recursion — take/skip every item: O(2^n) time, O(n) stack.
2. Memoised on (i, c) — O(n * cap) time and space (pseudo-polynomial: cap is a value,
   not an input length).
3. Bottom-up table — O(n * cap) time and space; supports reconstruction.
4. One row — iterate c from cap DOWN to w so best[c - w] is still the previous item's
   row: O(n * cap) time, O(cap) space. Iterating UP lets an item be reused, which is
   exactly `knapsack_unbounded`.
min_coins — state: fewest(x); transition: 1 + min(fewest(x - c)); base fewest(0) = 0.
Recursion O(k^amount) -> memo/table O(amount * k) time, O(amount) space (the table
is already one-dimensional). The coin memos recurse ~amount/min(coins) deep (up to
10^4): recursion depth ~amount hits the ~1000 limit (section 7.21) well inside the
constraints; this is why we move to the table. (The knapsack memo is only n <= 100 deep.)
Greedy is wrong for non-canonical coin systems (section 20.7).
Counting ways — coins in the OUTER loop counts combinations (each multiset is built in
one fixed coin order); amount in the outer loop counts permutations. Both O(amount * k).

Hints
-----
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
    def best(i: int, room: int) -> int:         # items[i:] with `room` capacity left
        if i == len(items):
            return 0
        w, v = items[i]
        skip = best(i + 1, room)
        return max(skip, v + best(i + 1, room - w)) if w <= room else skip

    return best(0, cap)


def knapsack_memo(items: list[Item], cap: int) -> int:
    @cache
    def best(i: int, room: int) -> int:
        if i == len(items):
            return 0
        w, v = items[i]
        skip = best(i + 1, room)
        return max(skip, v + best(i + 1, room - w)) if w <= room else skip

    return best(0, cap)


def knapsack_table(items: list[Item], cap: int) -> tuple[int, list[int]]:
    n = len(items)
    best = [[0] * (cap + 1) for _ in range(n + 1)]
    for i, (w, v) in enumerate(items, start=1):
        for c in range(cap + 1):
            best[i][c] = best[i - 1][c]
            if w <= c:
                best[i][c] = max(best[i][c], v + best[i - 1][c - w])
    chosen, c = [], cap
    for i in range(n, 0, -1):                   # value changed => item i-1 was taken
        if best[i][c] != best[i - 1][c]:
            chosen.append(i - 1)
            c -= items[i - 1][0]
    return best[n][cap], chosen[::-1]


def knapsack(items: list[Item], cap: int) -> int:
    best = [0] * (cap + 1)
    for w, v in items:
        for c in range(cap, w - 1, -1):         # DOWN: best[c - w] is still "without item"
            best[c] = max(best[c], v + best[c - w])
    return best[cap]


def knapsack_unbounded_brute(items: list[Item], cap: int) -> int:
    return max([0] + [v + knapsack_unbounded_brute(items, cap - w) for w, v in items if w <= cap])


def knapsack_unbounded(items: list[Item], cap: int) -> int:
    best = [0] * (cap + 1)
    for w, v in items:
        for c in range(w, cap + 1):             # UP: best[c - w] may already include this item
            best[c] = max(best[c], v + best[c - w])
    return best[cap]


# ---------------------------------------------------------------- coin change
def greedy_coins(coins: list[int], amount: int) -> int:
    """Wrong-but-tempting: largest coin first. Optimal only for canonical systems."""
    count = 0
    for c in sorted(coins, reverse=True):
        take, amount = divmod(amount, c)
        count += take
    return count if amount == 0 else -1


def min_coins_brute(coins: list[int], amount: int) -> int:
    inf = float("inf")

    def fewest(x: int) -> float:
        if x == 0:
            return 0
        return min([1 + fewest(x - c) for c in coins if c <= x], default=inf)

    r = fewest(amount)
    return -1 if r == inf else int(r)


def min_coins_memo(coins: list[int], amount: int) -> int:
    inf = float("inf")

    @cache
    def fewest(x: int) -> float:
        if x == 0:
            return 0
        return min([1 + fewest(x - c) for c in coins if c <= x], default=inf)

    r = fewest(amount)
    return -1 if r == inf else int(r)


def min_coins(coins: list[int], amount: int) -> int:
    sentinel = amount + 1                       # more coins than any real answer
    fewest = [0] + [sentinel] * amount
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x and fewest[x - c] + 1 < fewest[x]:
                fewest[x] = fewest[x - c] + 1
    return -1 if fewest[amount] == sentinel else fewest[amount]


# ---------------------------------------------------------------- counting ways
def count_combinations_brute(coins: list[int], amount: int) -> int:
    def ways(i: int, x: int) -> int:            # use coins[i:] only, in that order
        if x == 0:
            return 1
        if i == len(coins):
            return 0
        c = coins[i]
        return ways(i + 1, x) + (ways(i, x - c) if c <= x else 0)

    return ways(0, amount)


def count_combinations_memo(coins: list[int], amount: int) -> int:
    @cache
    def ways(i: int, x: int) -> int:
        if x == 0:
            return 1
        if i == len(coins):
            return 0
        c = coins[i]
        return ways(i + 1, x) + (ways(i, x - c) if c <= x else 0)

    return ways(0, amount)


def count_combinations(coins: list[int], amount: int) -> int:
    ways = [1] + [0] * amount
    for c in coins:                             # coin OUTER: each multiset counted once
        for x in range(c, amount + 1):
            ways[x] += ways[x - c]
    return ways[amount]


def count_permutations_brute(coins: list[int], amount: int) -> int:
    if amount == 0:
        return 1
    return sum(count_permutations_brute(coins, amount - c) for c in coins if c <= amount)


def count_permutations(coins: list[int], amount: int) -> int:
    ways = [1] + [0] * amount
    for x in range(1, amount + 1):              # amount OUTER: last coin can be any coin
        for c in coins:
            if c <= x:
                ways[x] += ways[x - c]
    return ways[amount]


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
