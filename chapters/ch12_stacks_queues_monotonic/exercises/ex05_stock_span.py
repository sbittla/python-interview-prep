"""
Exercise 05 — Online Stock Span                               [Tier: ★ Core]
Chapter 12 · Pattern: monotonic stack (online, with merged counts) · Target time: 20 min

Problem
-------
Prices arrive one per day. Build ``StockSpanner`` whose ``next(price) -> int`` returns today's
*span*: the number of consecutive days ending today (today included) on which the price was
less than or equal to today's price. Also provide ``spans(prices)`` for a whole list.

Examples
--------
>>> spans([100, 80, 60, 70, 60, 75, 85])
[1, 1, 1, 2, 1, 4, 6]

Constraints
-----------
- Up to 10**5 calls; prices are positive integers.

Hints
-----
- Days dominated by today's price can never block a future day.
- Store (price, span) pairs and merge the spans of everything you pop.

Wrong-but-tempting
------------------
- Popping on ``<`` instead of ``<=``: equal prices then block the span.
- Forgetting to add the popped spans (``span += popped_span``), which returns only the count
  of popped entries rather than the number of days they represent.
- Claiming O(1) worst case per call: a single call can pop O(n) entries; the bound is
  amortised.

Follow-ups
----------
- Previous greater element is the same stack: the top after popping is the "blocker" day.
- Span in a sliding window of the last k days only: cap with ``min(span, k)``.
"""
from __future__ import annotations


class NaiveSpanner:
    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def next(self, price: int) -> int:
        raise NotImplementedError("TODO")


class StockSpanner:
    def __init__(self) -> None:
        raise NotImplementedError("TODO")

    def next(self, price: int) -> int:
        raise NotImplementedError("TODO")


def brute_force(prices: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def spans(prices: list[int]) -> list[int]:
    raise NotImplementedError("TODO")


def main() -> None:
    spanner = StockSpanner()
    prices = [100, 80, 60, 70, 60, 75, 85]
    for p in prices:
        s = spanner.next(p)
        print(f"price {p:>3} -> span {s}   stack {spanner._stack}")
    for case in (prices, [1, 2, 3, 4], [4, 3, 2, 1], [5, 5, 5], [7]):
        print(f"{case!s:<34} -> {spans(case)}  agree={spans(case) == brute_force(case)}")


if __name__ == "__main__":
    main()
