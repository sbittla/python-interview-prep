"""
Exercise 09 — Stock Trading with Cooldown (state machine DP)        [Tier: ◆ Extended]
Chapter 19 · Pattern: state machine DP · Target time: 30 min

Problem
-------
prices[i] is a share's price on day i. You may hold at most one share, may trade as
often as you like, but after a sell you must sit out the next day (no buy the day
after selling). Return the maximum total profit.

Examples
--------
>>> max_profit([1, 2, 3, 0, 2])
3
>>> max_profit([5, 4, 3]), max_profit([])
(0, 0)

Constraints
-----------
- 0 <= len(prices) <= 10^5, 0 <= prices[i] <= 10^4.

Approach ladder
---------------
States at the end of a day:

    rest ---buy---> hold ---sell---> sold
    (wait)          (wait)             |
      ^------------ cooldown ----------+

Recipe — state: (day, holding); transition: holding -> keep or sell (sell jumps to
day + 2: the cooldown); not holding -> wait or buy; base: past the last day earns 0;
order: day descending; answer: best(0, not holding).
1. Plain recursion — two choices per day: O(2^n) time, O(n) stack.
2. Memoised on (day, holding) — 2n states: O(n) time, O(n) space; recursion depth ~n:
   hits the ~1000 limit (section 7.21) well inside the constraints; this is why we move to the table.
3. Bottom-up table — arrays hold[i], free[i] filled right to left: O(n), O(n).
4. Three variables (hold, sold, rest) updated left to right — each day reads only the
   previous day: O(n) time, O(1) space.

Hints
-----
- Name the states first (draw the arrows), then each update is one max per state.
- Update all three states from the OLD values (tuple assignment), or you will buy and
  sell on the same day.
- hold starts at -infinity: you cannot own a share before day 0.

Follow-ups
----------
- Transaction fee instead of cooldown: sold = hold + p - fee, no cooldown state.
- At most k transactions: add k to the state, O(nk).
"""
from __future__ import annotations

from functools import cache


def max_profit_brute(prices: list[int]) -> int:
    def best(i: int, holding: bool) -> int:
        if i >= len(prices):
            return 0
        if holding:                             # keep, or sell and skip tomorrow
            return max(best(i + 1, True), prices[i] + best(i + 2, False))
        return max(best(i + 1, False), -prices[i] + best(i + 1, True))

    return best(0, False)


def max_profit_memo(prices: list[int]) -> int:
    @cache
    def best(i: int, holding: bool) -> int:
        if i >= len(prices):
            return 0
        if holding:
            return max(best(i + 1, True), prices[i] + best(i + 2, False))
        return max(best(i + 1, False), -prices[i] + best(i + 1, True))

    return best(0, False)


def max_profit_table(prices: list[int]) -> int:
    n = len(prices)
    hold = [0] * (n + 2)                        # best from day i onward, holding a share
    free = [0] * (n + 2)                        # best from day i onward, not holding
    for i in range(n - 1, -1, -1):
        hold[i] = max(hold[i + 1], prices[i] + free[i + 2])
        free[i] = max(free[i + 1], -prices[i] + hold[i + 1])
    return free[0]


def max_profit(prices: list[int]) -> int:
    hold, sold, rest = float("-inf"), 0, 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return int(max(sold, rest))


def main() -> None:
    for prices in ([1, 2, 3, 0, 2], [5, 4, 3], [1, 4], [2, 1, 4, 5, 2, 9, 7], [3], []):
        rungs = (max_profit_brute(prices), max_profit_memo(prices), max_profit_table(prices),
                 max_profit(prices))
        print(f"max_profit({prices}) = {rungs[-1]}  rungs agree: {len(set(rungs)) == 1}")
    # trace of the three states on the first example
    hold, sold, rest = float("-inf"), 0, 0
    for day, p in enumerate([1, 2, 3, 0, 2]):
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
        print(f"  day {day} price {p}: hold={hold:>4} sold={sold:>4} rest={rest:>2}")


if __name__ == "__main__":
    main()
