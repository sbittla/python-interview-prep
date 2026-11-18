"""
Exercise 06 — CSV in, JSON out                                 [Tier: ★ Core]
Chapter 26 · Pattern: parse → validate → aggregate → serialise · Target time: 25 min

Problem
-------
``data/orders.csv`` has the header
``order_id,customer,item,quantity,unit_price,order_date``. Some fields contain quoted commas and one
row has a non-numeric quantity.

1. ``load_orders(path)`` returns ``(orders, bad_rows)``: ``orders`` is a list of dicts with typed
   values (``int`` id and quantity, ``Decimal`` unit price, ``datetime.date`` order date);
   ``bad_rows`` lists ``(line_number, reason)`` for rows that failed conversion.
2. ``revenue_by_customer(orders)`` returns ``{customer: Decimal total}`` sorted by customer name.
3. ``to_json(report)`` serialises a report containing ``Decimal`` and ``date`` values to a JSON
   string with sorted keys and 2-space indent (``Decimal`` → string such as ``"59.97"``,
   ``date`` → ISO string).
4. ``write_csv(path, rows)`` writes dict rows with ``csv.DictWriter`` (header first).

Examples
--------
>>> orders, bad = load_orders(DATA)
>>> len(orders), bad
(5, [(5, "quantity: invalid literal for int() with base 10: 'two'")])

Constraints
-----------
- Money must not be summed as ``float`` (``0.1 + 0.2 != 0.3``).
- Open CSV files with ``newline=""`` and an explicit encoding.

Approach ladder
---------------
1. Brute force — ``line.split(",")``: breaks on ``"Widget, large"``.
2. Improved   — ``csv.reader`` handles quoting, but positional indexes are fragile when columns move.
3. Optimal    — ``csv.DictReader`` + per-field converters, collecting bad rows instead of crashing;
   ``json.dumps(default=...)`` for types JSON does not know.

Hints
-----
- ``DictReader.line_num`` gives the current physical line number of the source file.
- ``json.dumps(obj, default=fn)`` calls ``fn`` for any object it cannot serialise.
- ``Decimal("19.99") * 3 == Decimal("59.97")``.

Follow-ups
----------
- How would you process a 10 GB CSV? (Stream rows; aggregate incrementally; never build a list.)
- JSON Lines vs one big JSON array — when is each better?
"""
from __future__ import annotations

import csv
import json
import tempfile
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "orders.csv"

CONVERTERS = {
    "order_id": int,
    "quantity": int,
    "unit_price": Decimal,
    "order_date": date.fromisoformat,
}


def load_orders(path: Path) -> tuple[list[dict], list[tuple[int, str]]]:
    orders, bad_rows = [], []
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                typed = dict(row)
                for field, convert in CONVERTERS.items():
                    try:
                        typed[field] = convert(row[field])
                    except Exception as exc:  # converter-specific errors vary (ValueError, InvalidOperation)
                        raise ValueError(f"{field}: {exc}") from exc
            except ValueError as exc:
                bad_rows.append((reader.line_num, str(exc)))
                continue
            orders.append(typed)
    return orders, bad_rows


def revenue_by_customer(orders: list[dict]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = defaultdict(Decimal)
    for order in orders:
        totals[order["customer"]] += order["quantity"] * order["unit_price"]
    return dict(sorted(totals.items()))


def _json_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"not JSON serialisable: {type(obj).__name__}")


def to_json(report) -> str:
    return json.dumps(report, default=_json_default, sort_keys=True, indent=2)


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    orders, bad = load_orders(DATA)
    print(f"loaded {len(orders)} orders, {len(bad)} bad row(s)")
    for line, reason in bad:
        print(f"  line {line}: {reason}")
    first = orders[0]
    print("first order:", {k: first[k] for k in ("order_id", "item", "unit_price", "order_date")})
    print("types:", {k: type(v).__name__ for k, v in first.items()})

    totals = revenue_by_customer(orders)
    print("\nrevenue_by_customer:")
    for customer, total in totals.items():
        print(f"  {customer:<10} {total:>8}")
    print("float pitfall: 0.1 + 0.2 == 0.3 ->", 0.1 + 0.2 == 0.3,
          "| Decimal ->", Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))

    report = {
        "generated_for": date(2026, 1, 31),
        "revenue": totals,
        "bad_rows": bad,
        "top_customer": max(totals, key=totals.get),
    }
    text = to_json(report)
    print("\nJSON report:")
    print(text)

    with tempfile.TemporaryDirectory() as tmp:
        out_json = Path(tmp) / "report.json"
        out_json.write_text(text, encoding="utf-8")
        back = json.loads(out_json.read_text(encoding="utf-8"))
        print("\nround-trip: revenue values are now", type(back["revenue"]["Globex"]).__name__,
              "and tuples became", type(back["bad_rows"][0]).__name__)

        out_csv = Path(tmp) / "revenue.csv"
        write_csv(out_csv, [{"customer": c, "revenue": t} for c, t in totals.items()])
        print("\nrevenue.csv:")
        print(out_csv.read_text(encoding="utf-8").replace("\r\n", "\n"), end="")


if __name__ == "__main__":
    main()
