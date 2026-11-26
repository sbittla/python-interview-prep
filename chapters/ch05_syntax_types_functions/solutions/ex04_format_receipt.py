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

Approach ladder
---------------
1. Brute force — pad with ``str.ljust``/``str.rjust`` and format numbers with ``round`` and
   manual comma insertion. O(n) time too, but long and error-prone.
2. Optimal    — one f-string per line using format specs: ``{name:<12.12}`` (left, width 12,
   truncate to 12), ``{qty:>5}``, ``{amount:>12,.2f}``. O(n) time. The format mini-language is
   the tool; knowing it is the point of this exercise.

Follow-ups
----------
- Money should not be a float in production: use ``decimal.Decimal`` (§7.8).
- Make the column widths parameters: nested replacement fields ``{name:<{w}}`` work.
"""
from __future__ import annotations


def brute_force(items: list[tuple[str, int, float]]) -> list[str]:
    def money(x: float) -> str:
        whole, frac = f"{round(x, 2):.2f}".split(".")
        groups = []
        while len(whole) > 3:
            groups.insert(0, whole[-3:])
            whole = whole[:-3]
        groups.insert(0, whole)
        return ",".join(groups) + "." + frac

    lines = ["Item".ljust(12) + "Qty".rjust(5) + "Amount".rjust(12)]
    total = 0.0
    for name, qty, price in items:
        amount = qty * price
        total += amount
        lines.append(name[:12].ljust(12) + str(qty).rjust(5) + money(amount).rjust(12))
    lines.append("TOTAL".ljust(17) + money(total).rjust(12))
    return lines


def solve(items: list[tuple[str, int, float]]) -> list[str]:
    lines = [f"{'Item':<12}{'Qty':>5}{'Amount':>12}"]
    total = 0.0
    for name, qty, price in items:
        amount = qty * price
        total += amount
        lines.append(f"{name:<12.12}{qty:>5}{amount:>12,.2f}")
    lines.append(f"{'TOTAL':<17}{total:>12,.2f}")
    return lines


def main() -> None:
    items = [("apple", 3, 0.5), ("laptop", 1, 1299.99), ("extra-long-product-name", 2, 2.25)]
    for line in solve(items):
        print(line)
    print("brute agrees:", brute_force(items) == solve(items))
    print("empty receipt:", solve([]))


if __name__ == "__main__":
    main()
