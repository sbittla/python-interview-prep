"""
Exercise 04 — Fix a Generated Average (Float Rounding, Empty Input) [Tier: ◆ Extended]
Chapter 46 · Pattern: edge-case table + exact oracle → fix · Target time: 20 min

Problem
-------
Spec: mean_price(prices) takes prices as decimal strings ("2.675"), each
non-negative with at most 3 decimal places, and returns their mean rounded
HALF UP to cents as a string ("2.68"). An empty list returns None.

The generated one-liner (below, given) passes "1.00, 2.00 -> 1.50". It fails
the spec on two counts: floats cannot hold most decimal prices exactly, and
round() rounds halves to even (→ §7.8, §7.9). It also crashes on [].

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

Approach ladder
---------------
1. Brute force — try a round number or two: both float and Decimal agree.
2. Improved   — an edge-case table aimed at the two known traps (halves and
   non-representable decimals) plus the empty list. Cheap and targeted.
3. Optimal    — table plus a seeded property check of mean_price against an
   exact Fraction oracle on random 3-decimal prices. Fix: Decimal(str) is
   exact; sum exactly; divide; quantize(Decimal("0.01"), ROUND_HALF_UP).
   O(n) time, O(1) extra space beyond the input.

Exactness note: Decimal division rounds to 28 significant digits. The exact
mean is either exactly on a half cent or at least 1/(1000 n) away from one,
so the rounding cannot cross a half cent while the total stays below about
10**24. The tests confirm agreement with the exact oracle on random inputs.

Follow-ups
----------
- Negative prices (refunds)? "Half up" becomes ambiguous: ROUND_HALF_UP
  rounds away from zero; ask which the business wants.
- Money in integer cents end to end avoids most of this; the input format
  here (3 decimals) forces exact decimal arithmetic.
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
    try:
        return fn(prices)
    except Exception as exc:
        return f"raises {type(exc).__name__}"


EDGE_CASES: list[tuple[list[str], str | None]] = [
    ([], None),                          # empty input
    (["0.125"], "0.13"),                 # exact half cent: half up, not half even
    (["1.005"], "1.01"),                 # float 1.005 is just below 1.005
    (["2.675"], "2.68"),                 # same trap, different digits
    (["0.01", "0.02"], "0.02"),          # mean 0.015 is a half cent
    (["1.00", "1.00", "2.00"], "1.33"),  # 1.333...: not a terminating decimal
]


def failures(fn, cases) -> list[tuple[list[str], str | None, object]]:
    return [(p, want, got) for p, want in cases if (got := outcome(fn, p)) != want]


def oracle(prices: list[str]) -> str | None:
    if not prices:
        return None
    mean = sum(Fraction(p) for p in prices) / len(prices)
    cents = math.floor(mean * 100 + Fraction(1, 2))   # half up for mean >= 0
    return f"{cents // 100}.{cents % 100:02d}"


# --- the fix ---------------------------------------------------------------------------
def mean_price(prices: list[str]) -> str | None:
    if not prices:
        return None
    total = sum((Decimal(p) for p in prices), Decimal(0))     # exact
    mean = total / len(prices)
    return str(mean.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


COMPLEXITY = {"time": "O(n)", "space": "O(1)"}


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
