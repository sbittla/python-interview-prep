"""
Exercise 05 — Pair-Programming Kata: Checkout, v1 → v2 → v3        [Tier: ★ Core]
Chapter 32 · Pattern: incremental requirements, rules as data · Target time: 45 min

Problem
-------
The interviewer reveals the spec one version at a time; each version must keep
every earlier test passing. Prices are integer cents.

v1  total_v1(skus, prices) -> int. skus is the scan order, e.g. ["A", "B", "A"].
    An unknown SKU raises ValueError("unknown SKU 'X'"). Empty basket -> 0.
v2  total_v2(skus, prices, offers) adds multi-buy offers {sku: (qty, price)}:
    "3 A for 130". Each full group of qty costs price; the rest pay unit price.
v3  Checkout(prices, rules) with scan(sku), total() and receipt(). Rules are
    pluggable: item rules (MultiBuy) are applied first, then basket rules
    (PercentOff(percent, min_subtotal)): percent off the post-offer subtotal
    when it is at least min_subtotal, rounded down to whole cents (customer's favour).
    receipt() lists "sku x qty  cents" lines (sorted by SKU), then one line per
    discount (negative), then TOTAL.
    Bad rules fail fast, at construction, with ValueError: MultiBuy qty <= 0 or
    price < 0; PercentOff percent outside 0..100 or min_subtotal < 0; and, in
    Checkout(prices, rules), a MultiBuy for an unpriced SKU or one whose price is
    above qty x unit price (an "offer" that charges more).

Examples
--------
>>> PRICES = {"A": 50, "B": 30, "C": 20}
>>> total_v1(["A", "B", "A"], PRICES)
130
>>> total_v2(["A", "A", "A", "A"], PRICES, {"A": (3, 130)})
180
>>> co = Checkout(PRICES, [MultiBuy("A", 3, 130), PercentOff(10, 200)])
>>> for s in "AAAABB": co.scan(s)
>>> co.total()            # 240 after multi-buy, then 10% off
216

Constraints
-----------
- Order of scanning never changes the total.
- v1 behaviour is v3 with no rules: Checkout(prices).total() == total_v1(...).

Approach ladder
---------------
1. Brute force — grow one function with an if per new requirement; by v3
   offers and coupons interleave and ordering bugs appear.
2. Improved   — count SKUs with Counter (v2): offers become arithmetic
   (divmod) instead of re-scanning; O(n + distinct SKUs).
3. Optimal    — rules as small objects sharing one interface (stage, discount,
   label); Checkout sorts them by stage and lets each see the running subtotal.
   A new kind of offer = a new rule class; Checkout and existing tests stay
   untouched. ("Buy 2 get 1 free" is not new: it is MultiBuy(sku, 3, 2 * unit).)
   O(1) per scan, O(distinct SKUs + rules) per total().

Follow-ups
----------
- Two offers on one SKU ("3 for 130" and "5 for 200"): best combination is a
  small knapsack; say so, and ask whether it is in scope before building it.
- Remove an item (void a scan): Counter subtraction; guard against negatives.
- Should a percentage coupon apply before or after multi-buys? Ask: this is a
  business rule, not an engineering choice.
- Wrong but tempting: 10% of the GROSS (before multi-buys) over-discounts;
  round() instead of // rounds half to even (round(24.5) == 24, round(25.5) == 26);
  two MultiBuy rules on one SKU both fire on the same items.

Edge cases
----------
- Empty basket; unknown SKU (scan or rule); subtotal exactly on the threshold;
  15% of an odd subtotal (rounding); scan order; invalid rule parameters.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar, Protocol


def _check_known(skus: Iterable[str], prices: dict[str, int]) -> Counter[str]:
    counts = Counter(skus)
    for sku in sorted(counts):
        if sku not in prices:
            raise ValueError(f"unknown SKU {sku!r}")
    return counts


# --- v1 -----------------------------------------------------------------------
def total_v1(skus: Iterable[str], prices: dict[str, int]) -> int:
    counts = _check_known(skus, prices)
    return sum(prices[s] * n for s, n in counts.items())


# --- v2 -----------------------------------------------------------------------
def total_v2(skus: Iterable[str], prices: dict[str, int],
             offers: dict[str, tuple[int, int]]) -> int:
    counts = _check_known(skus, prices)
    total = 0
    for sku, n in counts.items():
        if sku in offers:
            qty, price = offers[sku]
            groups, rest = divmod(n, qty)
            total += groups * price + rest * prices[sku]
        else:
            total += n * prices[sku]
    return total


# --- v3 -----------------------------------------------------------------------
class Rule(Protocol):
    stage: ClassVar[int]              # 0 = item rules, 1 = basket rules

    def discount(self, counts: Counter[str], prices: dict[str, int], subtotal: int) -> int: ...
    def label(self) -> str: ...
    def check(self, prices: dict[str, int]) -> None: ...


@dataclass(frozen=True)
class MultiBuy:                       # item rule: "qty of sku for price"
    sku: str
    qty: int
    price: int
    stage: ClassVar[int] = 0

    def __post_init__(self) -> None:
        if self.qty <= 0 or self.price < 0:
            raise ValueError(f"bad offer {self.label()!r}: qty must be > 0, price >= 0")

    def check(self, prices: dict[str, int]) -> None:
        if self.sku not in prices:
            raise ValueError(f"offer for unknown SKU {self.sku!r}")
        if self.price > self.qty * prices[self.sku]:
            raise ValueError(f"offer {self.label()!r} costs more than {self.qty} singles")

    def discount(self, counts: Counter[str], prices: dict[str, int], subtotal: int) -> int:
        return counts[self.sku] // self.qty * (self.qty * prices[self.sku] - self.price)

    def label(self) -> str:
        return f"{self.qty} {self.sku} for {self.price}"


@dataclass(frozen=True)
class PercentOff:                     # basket rule: percent off at a threshold
    percent: int
    min_subtotal: int
    stage: ClassVar[int] = 1

    def __post_init__(self) -> None:
        if not 0 <= self.percent <= 100 or self.min_subtotal < 0:
            raise ValueError(f"bad coupon {self.label()!r}")

    def check(self, prices: dict[str, int]) -> None:
        pass                                   # basket rules need no price lookups

    def discount(self, counts: Counter[str], prices: dict[str, int], subtotal: int) -> int:
        return subtotal * self.percent // 100 if subtotal >= self.min_subtotal else 0

    def label(self) -> str:
        return f"{self.percent}% off over {self.min_subtotal}"


class Checkout:
    def __init__(self, prices: dict[str, int], rules: Iterable[Rule] = ()) -> None:
        self.prices = prices
        self.rules = sorted(rules, key=lambda r: r.stage)   # stable: item rules first
        for rule in self.rules:
            rule.check(prices)                                # fail fast, not at total()
        self.counts: Counter[str] = Counter()

    def scan(self, sku: str) -> None:
        if sku not in self.prices:
            raise ValueError(f"unknown SKU {sku!r}")
        self.counts[sku] += 1

    def _gross(self) -> int:
        return sum(self.prices[s] * n for s, n in self.counts.items())

    def _discounts(self) -> list[tuple[str, int]]:
        """(label, -cents) per rule that fired; each rule sees the running subtotal."""
        subtotal, lines = self._gross(), []
        for rule in self.rules:
            off = rule.discount(self.counts, self.prices, subtotal)
            if off:
                lines.append((rule.label(), -off))
                subtotal -= off
        return lines

    def total(self) -> int:
        return self._gross() + sum(d for _, d in self._discounts())

    def receipt(self) -> str:
        rows = [(f"{s} x {n}", self.prices[s] * n) for s, n in sorted(self.counts.items())]
        rows += self._discounts() + [("TOTAL", self.total())]
        return "\n".join(f"{label:<18} {cents:>6}" for label, cents in rows)


def main() -> None:
    prices = {"A": 50, "B": 30, "C": 20}
    print("v1:", total_v1("ABA", prices), total_v1([], prices))
    try:
        total_v1("AZ", prices)
    except ValueError as exc:
        print("v1 unknown:", exc)
    offers = {"A": (3, 130), "B": (2, 45)}
    for basket in ("AAA", "AAAA", "AAAAAABB", "BAB"):
        print(f"v2 {basket}: {total_v2(basket, prices, offers)}")
    rules = [MultiBuy("A", 3, 130), MultiBuy("B", 2, 45), PercentOff(10, 200)]
    co = Checkout(prices, rules)
    for sku in "BAACABA":
        co.scan(sku)
    print("v3 receipt:")
    print(co.receipt())
    small = Checkout(prices, rules)
    for sku in "AAAB":
        small.scan(sku)
    print("v3 AAAB:", small.total(), "(subtotal 160 is under the 200 threshold)")
    plain = Checkout(prices)
    for sku in "ABA":
        plain.scan(sku)
    print("v3 with no rules equals v1:", plain.total() == total_v1("ABA", prices))

if __name__ == "__main__":
    main()
