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

Hints
-----
- The memoised rung recurses ~n deep and hits the ~1000 limit (section 7.21) well inside
  the constraints; this is why the final answer is a table.
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
    raise NotImplementedError("TODO")


def max_profit_memo(prices: list[int]) -> int:
    raise NotImplementedError("TODO")


def max_profit_table(prices: list[int]) -> int:
    raise NotImplementedError("TODO")


def max_profit(prices: list[int]) -> int:
    raise NotImplementedError("TODO")


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
