"""
Exercise 04 — CSV to Nested JSON, and Nested JSON Back to CSV   [Tier: ★ Core]
Chapter 30 · Pattern: csv.DictReader -> group -> json.dumps; recursive flatten · Target time: 25 min

Problem
-------
1. `orders_to_customers(rows)` — rows are dicts from `csv.DictReader` over
   `data/orders.csv` (order_id, customer, country, item, qty, unit_price). Return
   {customer: {"country": str | None, "orders": int, "total_cents": int, "items": [sorted]}}
   with customers sorted by name. Money is exact: parse "19.99" to 1999 cents, never float.
   An empty country becomes None (JSON null).
2. `flatten(obj)` — turn nested dicts/lists into one flat dict with dotted keys:
   {"a": {"b": 1}, "c": [5, 6]} -> {"a.b": 1, "c.0": 5, "c.1": 6}.
3. `to_csv(records)` — write flat dicts to a CSV string; the header is the sorted union of
   all keys, missing cells are empty.

Examples
--------
>>> to_cents("19.99"), to_cents("5.5"), to_cents("12")
(1999, 550, 1200)
>>> flatten({"a": {"b": 1}, "c": [5, {"d": None}]})
{'a.b': 1, 'c.0': 5, 'c.1.d': None}

Constraints
-----------
- Quoted fields may contain commas and doubled quotes (`""USB-C""`): use the csv
  module, never `line.split(",")`.
- Prices have at most 2 decimal places.

Hints
-----
- Open CSV files with `newline=""` so the csv module handles embedded newlines (→ §26.5).
- `Decimal("19.99") * 100` is exactly 1999; `int(...)` of it is safe.
- `csv.DictWriter(buf, fieldnames=..., restval="")` fills missing keys.

Edge cases
----------
- Quoted comma, doubled quote, empty country, the same item ordered twice, empty input,
  empty nested containers in flatten ({} and [] produce no keys).

Follow-ups
----------
- Very large CSV: stream rows and keep only per-customer accumulators (O(customers) memory).
- JSON Lines output: one `json.dumps(record)` per line, appendable and streamable.
- Keys that contain "." already: choose an escape or use tuple paths.
"""
from __future__ import annotations

import csv
import io
import json
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

DATA = Path(__file__).resolve().parent.parent / "data"


def to_cents(price: str) -> int:
    raise NotImplementedError("TODO")


def naive_split(line: str) -> list[str]:
    """Rung 1, shown only to fail: splits inside quoted fields."""
    return line.rstrip("\n").split(",")


def orders_to_customers(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, Any]]:
    raise NotImplementedError("TODO")


def flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
    raise NotImplementedError("TODO")


def to_csv(records: list[dict[str, Any]]) -> str:
    raise NotImplementedError("TODO")


def main() -> None:
    path = DATA / "orders.csv"
    with open(path, encoding="utf-8") as f:
        line = f.readlines()[1]
    print("naive split of row 1:", naive_split(line), "->", len(naive_split(line)), "fields")
    print("float money: 0.10 * 3 =", 0.10 * 3, "| cents:", 3 * to_cents("0.10"))
    with open(path, encoding="utf-8", newline="") as f:
        customers = orders_to_customers(csv.DictReader(f))
    text = json.dumps(customers, indent=2, sort_keys=True)
    print(text)
    print("round-trips:", json.loads(text) == customers)
    nested = [{"id": 1, "user": {"name": "Asha", "tags": ["a", "b"]}},
              {"id": 2, "user": {"name": "Bo"}, "extra": {}}]
    flat = [flatten(r) for r in nested]
    print("flat:", flat)
    print(to_csv(flat), end="")
    print("empty:", orders_to_customers([]), flatten({}), repr(to_csv([])))


if __name__ == "__main__":
    main()
