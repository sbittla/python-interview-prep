"""
Exercise 04 — Format an Aligned Receipt With f-strings        [Tier: ★ Core]
Chapter 05 · Pattern: string formatting · Target time: 15 min

Problem
-------
Given a list of ``(name, quantity, unit_price)`` tuples, return the lines of a plain-text
receipt as a list of strings (every line is 29 characters wide while the numbers fit):

- a header line: ``Item`` left-aligned in 12 columns, ``Qty`` right-aligned in 5, ``Amount``
  right-aligned in 12;
- one line per item: the name truncated to 12 characters and left-aligned, the quantity
  right-aligned in 5, and quantity * unit_price right-aligned in 12 with a thousands separator
  and exactly 2 decimals;
- a final ``TOTAL`` line with the grand total in the Amount column (``TOTAL`` padded to 17).

Examples
--------
>>> for line in solve([("apple", 3, 0.5), ("laptop", 1, 1299.99)]): print(line)
Item          Qty      Amount
apple           3        1.50
laptop          1    1,299.99
TOTAL                1,301.49

Constraints
-----------
- 0 <= len(items) <= 1000; quantities are non-negative ints; prices are non-negative floats

Hints
-----
1. Work out the three column widths and the width of the TOTAL label from the example.
2. ``brute_force``: ``str.ljust``/``str.rjust`` plus your own comma grouping.
3. ``solve``: the format mini-language has an alignment, a width, a *precision* (which also
   truncates strings) and a thousands-separator option. Combine them inside f-strings.
4. Compare both versions on the same input; they must be identical line by line.

Follow-ups
----------
- Money should not be a float in production: use ``decimal.Decimal`` (§7.8).
- Make the column widths parameters: nested replacement fields ``{name:<{w}}`` work.
"""
from __future__ import annotations


def brute_force(items: list[tuple[str, int, float]]) -> list[str]:
    raise NotImplementedError("TODO")


def solve(items: list[tuple[str, int, float]]) -> list[str]:
    raise NotImplementedError("TODO")


def main() -> None:
    items = [("apple", 3, 0.5), ("laptop", 1, 1299.99), ("extra-long-product-name", 2, 2.25)]
    for line in solve(items):
        print(line)
    print("brute agrees:", brute_force(items) == solve(items))
    print("empty receipt:", solve([]))


if __name__ == "__main__":
    main()
