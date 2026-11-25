"""
Exercise 04 — Refactor Legacy Code Behind Characterization Tests   [Tier: ★ Core]
Chapter 32 · Pattern: golden master → refactor → compare · Target time: 40 min

Problem
-------
shipping_cost_legacy (below, given) works in production but nobody wants to
touch it. Your pair asks you to make it readable without changing behaviour.

1. record(fn, cases) -> {case: outcome}. outcome is fn(*case), or the string
   "raises <ExceptionName>" if it raises. This is the golden master.
2. compare(old, new, cases) -> list of (case, old_outcome, new_outcome) for
   every case where they differ, in the order of `cases`. [] means "same".
3. default_grid() -> every combination of the boundary weights below with all
   zones (including an unknown one), express in (False, True), member in
   (False, True): 13 * 4 * 2 * 2 = 208 cases.
4. shipping_cost(grams, zone, express, member) -> the clean, table-driven
   version. compare(legacy, clean, default_grid()) must be [].

Behaviour to preserve (found by reading AND by the golden master):
- grams <= 0 returns 0 (does not raise);
- weight bills in whole kg, rounded up;
- any unknown zone is priced as international;
- express: domestic +1000 cents flat, other zones x1.5 rounded down;
- member discount of 500 only when the cost is strictly above 2000.

Examples
--------
>>> shipping_cost_legacy(1500, "eu", False, False), shipping_cost(1500, "eu", False, False)
(1250, 1250)
>>> compare(shipping_cost_legacy, shipping_cost, default_grid())
[]

Constraints
-----------
- Integer cents and grams throughout: float rounding would make "identical
  behaviour" depend on the order of arithmetic.

Hints
-----
- record: try fn(*case); on Exception store f"raises {type(exc).__name__}".
- WEIGHTS: read every literal in the legacy code (0, 1000 g per kg, 10 kg) and
  take each boundary and its neighbours, plus a few values in between: 13 values.
- default_grid: itertools.product(WEIGHTS, ZONES, (False, True), (False, True)).
- Refactor: put the per-zone numbers in a table (e.g. a small frozen dataclass
  per zone); decide how the unknown-zone and express rules fit into it.
- Run compare after every small step; an empty list is your green light.

Follow-ups
----------
- The grid is only as good as its boundaries: derive them from every literal
  in the legacy code (1000 g, 10 kg, 2000 cents).
- Behaviour changes ("unknown zone should raise") come in a SEPARATE commit,
  after the refactor, with the golden master updated on purpose.
- Random inputs (seeded) can complement the grid; see property-style tests.
"""
from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable
from dataclasses import dataclass

Case = tuple


# --- given: the legacy code (do not edit) -------------------------------------
def shipping_cost_legacy(g, z, e, m):
    if g <= 0:
        return 0
    k = (g + 999) // 1000
    if z == "domestic":
        if k <= 1:
            c = 500
        else:
            c = 500 + (k - 1) * 200
    elif z == "eu":
        if k <= 1:
            c = 900
        else:
            c = 900 + (k - 1) * 350
            if k > 10:
                c = c + 1000
    else:
        c = 1500 + k * 500
    if e:
        if z == "domestic":
            c = c + 1000
        else:
            c = c * 3 // 2
    if m:
        if c > 2000:
            c = c - 500
    return c


# --- given: a wrong refactor, used only to show that compare() catches it -----
def shipping_cost_tempting(grams: int, zone: str, express: bool, member: bool) -> int:
    """Wrong but tempting: a "tidy" rewrite that also changes two behaviours."""
    if grams <= 0:
        raise ValueError("weight must be positive")             # was: return 0
    kg = -(-grams // 1000)
    if zone == "domestic":
        cost = 500 + (kg - 1) * 200
    elif zone == "eu":
        cost = 900 + (kg - 1) * 350 + (1000 if kg > 10 else 0)
    else:
        cost = 1500 + kg * 500
    if express:
        cost = cost + 1000 if zone == "domestic" else cost * 3 // 2
    if member and cost >= 2000:                                 # was: strictly above
        cost -= 500
    return cost


# --- characterization harness ----------------------------------------------------
def record(fn: Callable[..., object], cases: Iterable[Case]) -> dict[Case, object]:
    raise NotImplementedError("TODO")


def compare(old: Callable[..., object], new: Callable[..., object],
            cases: Iterable[Case]) -> list[tuple[Case, object, object]]:
    raise NotImplementedError("TODO")


WEIGHTS: tuple[int, ...] = ()   # TODO: boundary weights in grams (see Hints)
ZONES = ("domestic", "eu", "intl", "mars")


def default_grid() -> list[Case]:
    raise NotImplementedError("TODO")


# --- the refactor ------------------------------------------------------------------
# TODO: your rate table (one entry per zone) and named constants go here.


def shipping_cost(grams: int, zone: str, express: bool, member: bool) -> int:
    """Shipping price in cents. Unknown zones are priced as "intl" (legacy behaviour)."""
    raise NotImplementedError("TODO")


def main() -> None:
    grid = default_grid()
    golden = record(shipping_cost_legacy, grid)
    print(f"golden master: {len(golden)} cases, {len(set(golden.values()))} distinct outcomes")
    for case in [(2000, "eu", False, False), (11000, "eu", True, True), (1, "mars", False, True)]:
        print(f"  legacy{case} = {golden[case]}")
    print("clean vs legacy mismatches:", compare(shipping_cost_legacy, shipping_cost, grid))
    diffs = compare(shipping_cost_legacy, shipping_cost_tempting, grid)
    print(f"tempting vs legacy mismatches: {len(diffs)}")
    for case, old, new in diffs[:2] + diffs[-2:]:
        print(f"  {case}: legacy={old!r} new={new!r}")


if __name__ == "__main__":
    main()
