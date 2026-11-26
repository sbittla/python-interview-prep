"""
Exercise 04 — Fix a Generated Average (Float Rounding, Empty Input) [Tier: ◆ Extended]
Chapter 46 · Pattern: edge-case table + exact oracle → fix · Target time: 20 min

Problem
-------
Spec: mean_price(prices) takes prices as decimal strings ("2.675"), each
non-negative with at most 3 decimal places, and returns their mean rounded
HALF UP to cents as a string ("2.68"). An empty list returns None.

The generated one-liner (below, given) passes "1.00, 2.00 -> 1.50". Find
every way it breaks the spec (→ §7.8, §7.9 if you need a nudge).

1. outcome(fn, prices) -> fn(prices), or "raises <ExceptionName>". Bug
   reports should show the crash, not stop at it.
2. EDGE_CASES: (prices, expected) pairs that a reviewer would ask about: the
   empty list, an exact half cent, a price whose float is just below the half
   cent, a mean that is not a terminating decimal. Each expected value must
   follow the spec (a test checks them against an exact oracle).
3. failures(fn, cases) -> [(prices, expected, outcome)] for every case fn gets
   wrong, in order.
4. oracle(prices) -> the spec with Fraction arithmetic (exact, independent of
   your fix). mean_price(prices) -> the fix with Decimal. COMPLEXITY.

Examples
--------
>>> generated_mean_price(["1.00", "2.00"]), generated_mean_price(["0.125"])
('1.50', '0.12')
>>> mean_price(["0.125"]), mean_price([])
('0.13', None)

Constraints
-----------
- Never convert a price to float.

Hints
-----
- In a REPL: round(0.125, 2), round(2.675, 2), Decimal(1.005) vs Decimal("1.005").
- Half up for a non-negative exact value q: floor(q * 100 + 1/2) cents.
- Decimal(str) is exact; look at Decimal.quantize and its rounding argument.
- Format cents as f"{cents // 100}.{cents % 100:02d}" in the oracle.
- Use := in a comprehension, or a plain loop, to call fn once per case.

Follow-ups
----------
- Negative prices (refunds)? What does "half up" mean then?
- Would integer cents end to end avoid the problem?
"""
from __future__ import annotations

import math
import random
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction


# --- given: the generated code (do not edit) -----------------------------------
def generated_mean_price(prices: list[str]) -> str | None:
    """AI-generated: mean of the prices, rounded to cents."""
    return f"{round(sum(float(p) for p in prices) / len(prices), 2):.2f}"


# --- your bug-finding tools --------------------------------------------------------
def outcome(fn, prices: list[str]) -> object:
    raise NotImplementedError("TODO")


EDGE_CASES: list[tuple[list[str], str | None]] = []   # TODO


def failures(fn, cases) -> list[tuple[list[str], str | None, object]]:
    raise NotImplementedError("TODO")


def oracle(prices: list[str]) -> str | None:
    raise NotImplementedError("TODO")


# --- the fix ---------------------------------------------------------------------------
def mean_price(prices: list[str]) -> str | None:
    raise NotImplementedError("TODO")


COMPLEXITY: dict[str, str] = {}   # TODO


def random_prices(rng: random.Random) -> list[str]:
    return [f"{rng.randint(0, 5000) / 1000:.3f}" for _ in range(rng.randint(1, 5))]


def main() -> None:
    print("happy path:", generated_mean_price(["1.00", "2.00"]))
    for prices, want, got in failures(generated_mean_price, EDGE_CASES):
        print(f"generated {prices}: want {want!r}, got {got!r}")
    print("fixed failures:", failures(mean_price, EDGE_CASES))
    rng = random.Random(0)
    cases = [random_prices(rng) for _ in range(2000)]
    print("random cases where generated != oracle:",
          sum(generated_mean_price(p) != oracle(p) for p in cases), "of", len(cases))
    print("random cases where fixed != oracle:",
          sum(mean_price(p) != oracle(p) for p in cases), "of", len(cases))
    print("complexity:", COMPLEXITY)


if __name__ == "__main__":
    main()
