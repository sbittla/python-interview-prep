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

Approach ladder
---------------
1. Brute force — keep every price; on each call walk back while ``prices[j] <= price``.
   O(n) per call, O(n^2) for a rising series.
2. Optimal    — keep a stack of ``(price, span)`` with strictly decreasing prices. A new
   price swallows every entry with price ``<=`` it, adding their spans to its own, then is
   pushed. A swallowed day can never be the "blocker" for a future day (today is at least as
   high and more recent), so discarding it is safe. Each day is pushed once and popped at most
   once: amortised O(1) per call, O(n) worst-case space.
   Why move up: the brute force re-walks the same days again and again; the stack compresses
   each run of dominated days into one entry.

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
        self._prices: list[int] = []

    def next(self, price: int) -> int:
        self._prices.append(price)
        span = 0
        for p in reversed(self._prices):
            if p > price:
                break
            span += 1
        return span


class StockSpanner:
    def __init__(self) -> None:
        self._stack: list[tuple[int, int]] = []    # (price, span); prices strictly decreasing

    def next(self, price: int) -> int:
        span = 1
        while self._stack and self._stack[-1][0] <= price:
            span += self._stack.pop()[1]           # absorb the dominated run
        self._stack.append((price, span))
        return span


def brute_force(prices: list[int]) -> list[int]:
    spanner = NaiveSpanner()
    return [spanner.next(p) for p in prices]


def spans(prices: list[int]) -> list[int]:
    spanner = StockSpanner()
    return [spanner.next(p) for p in prices]


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
