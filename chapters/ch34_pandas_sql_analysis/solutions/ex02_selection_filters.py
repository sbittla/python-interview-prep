"""
Exercise 02 — Selection with loc, iloc and Boolean Masks             [Tier: ★ Core]
Chapter 34 · Pattern: boolean mask = SQL WHERE, .loc assignment · Target time: 15 min

Problem
-------
Use `data/orders.csv` (order_id, user_id, order_date, amount, status).
1. `big_paid_orders(orders, min_amount, start, end)` — paid orders with
   amount >= min_amount and start <= order_date <= end (ISO date strings,
   inclusive). Return columns [order_id, user_id, amount], sorted by amount
   descending then order_id ascending, with a fresh 0..k-1 index.
   NaN amounts never qualify.
2. `sql_big_paid_orders(conn, ...)` — the same rows from SQLite table `orders`.
3. `label_vs_position(orders)` — sort by amount descending (NaN last, stable)
   WITHOUT resetting the index; return (order_id of ranked.loc[0], order_id of
   ranked.iloc[0]). loc[0] is the row LABELLED 0 (the first file row);
   iloc[0] is the first POSITION (the biggest order).
4. `flag_refund_risk(orders, user_ids)` — return a COPY with a new bool
   column `risk`, True for paid orders from `user_ids`; the input frame must
   not change. Use one .loc[mask, col] assignment, never chained indexing.

Examples
--------
>>> big_paid_orders(orders, 115, "2026-01-01", "2026-03-31")["order_id"].tolist()
[1015, 1008]

Constraints
-----------
- n <= 10**6 rows; the result must not depend on file order (sort it).

Approach ladder
---------------
1. Brute force — iterate rows with itertuples() and append matches: O(n)
   time but a Python-level loop (~100x slower constant), easy to forget NaN.
2. Optimal    — one boolean mask (&, |, ~ with parentheses), .loc[mask, cols],
   then sort_values: O(n) mask + O(k log k) sort of the k matches.
   Why move up: vectorised masks run in C and compose like SQL WHERE.

Hints
-----
- `&` binds tighter than `>=`: wrap each comparison in parentheses.
- Series.between(lo, hi) is inclusive on both ends by default.
- Comparisons with NaN are False, so `amount >= x` already drops NaN.
- Under copy-on-write (always on in pandas 3) `df[mask]["col"] = v` never
  modifies df; pandas warns with ChainedAssignmentError.

Follow-ups
----------
- `query("status == 'paid' and amount >= @m")` — same mask, string syntax.
- Select rows whose user_id is in a 10**5-element list: isin (hash set, O(n)).
- When does `df.loc[a:b]` include b? (Label slices are inclusive; iloc's are not.)
"""
from __future__ import annotations

import sqlite3
import warnings
from contextlib import closing
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)


def load_orders() -> pd.DataFrame:
    return pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"])


def brute_force_big_paid(orders: pd.DataFrame, min_amount: float, start: str, end: str) -> list[int]:
    lo, hi = pd.Timestamp(start), pd.Timestamp(end)
    hits = [(r.amount, r.order_id) for r in orders.itertuples()
            if r.status == "paid" and r.amount >= min_amount and lo <= r.order_date <= hi]
    return [oid for _, oid in sorted(hits, key=lambda t: (-t[0], t[1]))]


def big_paid_orders(orders: pd.DataFrame, min_amount: float, start: str, end: str) -> pd.DataFrame:
    mask = ((orders["status"] == "paid")
            & (orders["amount"] >= min_amount)
            & orders["order_date"].between(start, end))
    out = orders.loc[mask, ["order_id", "user_id", "amount"]]
    return out.sort_values(["amount", "order_id"], ascending=[False, True]).reset_index(drop=True)


SQL_BIG_PAID = """
SELECT order_id, user_id, amount
FROM orders
WHERE status = 'paid' AND amount >= :m AND order_date BETWEEN :start AND :end
ORDER BY amount DESC, order_id
"""


def sql_big_paid_orders(conn: sqlite3.Connection, min_amount: float, start: str, end: str) -> pd.DataFrame:
    return pd.read_sql_query(SQL_BIG_PAID, conn, params={"m": min_amount, "start": start, "end": end})


def label_vs_position(orders: pd.DataFrame) -> tuple[int, int]:
    ranked = orders.sort_values("amount", ascending=False, na_position="last", kind="stable")
    return int(ranked.loc[0, "order_id"]), int(ranked.iloc[0]["order_id"])


def flag_refund_risk(orders: pd.DataFrame, user_ids: list[int]) -> pd.DataFrame:
    out = orders.copy()
    out["risk"] = False
    out.loc[(out["status"] == "paid") & out["user_id"].isin(user_ids), "risk"] = True
    return out


def to_sqlite(orders: pd.DataFrame) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    table = orders.assign(order_date=orders["order_date"].dt.strftime("%Y-%m-%d"))
    table.to_sql("orders", conn, index=False)
    return conn


def main() -> None:
    orders = load_orders()
    res = big_paid_orders(orders, 100, "2026-01-01", "2026-03-31")
    print("paid, amount >= 100, Q1 2026:")
    print(res.to_string())
    with closing(to_sqlite(orders)) as conn:
        sql = sql_big_paid_orders(conn, 100, "2026-01-01", "2026-03-31")
    print("SQL matches pandas:", sql.equals(res))
    print("brute force matches:", brute_force_big_paid(orders, 100, "2026-01-01", "2026-03-31")
          == res["order_id"].tolist())
    print("nothing qualifies:", len(big_paid_orders(orders, 10_000, "2026-01-01", "2026-12-31")), "rows")
    by_loc, by_iloc = label_vs_position(orders)
    print(f"after sorting: loc[0] -> order {by_loc} (first file row), iloc[0] -> order {by_iloc} (biggest)")
    flagged = flag_refund_risk(orders, [2, 4])
    print("risk rows:", int(flagged["risk"].sum()), "| input untouched:", "risk" not in orders.columns)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        orders[orders["status"] == "paid"]["amount"] = 0.0     # chained assignment: a no-op
    print("chained assignment changed data:", bool((orders["amount"] == 0).any()),
          "| warning:", sorted({type(w.message).__name__ for w in caught}))


if __name__ == "__main__":
    main()
