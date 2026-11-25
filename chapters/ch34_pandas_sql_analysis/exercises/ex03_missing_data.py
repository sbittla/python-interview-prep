"""
Exercise 03 — Missing Data: Impute, Count, and NaN vs SQL NULL       [Tier: ★ Core]
Chapter 34 · Pattern: isna / fillna / groupby(dropna=False) · Target time: 20 min

Problem
-------
`orders.csv` has blank amounts and one exact duplicate row; `users.csv` has
users with a blank country.
1. `clean_orders(orders)` — drop exact duplicate rows; fill each missing
   amount with the median amount of that user's other orders, or the global
   median if the user has none; add a bool column `imputed`. Sort by
   order_id, fresh index. Do not modify the input.
2. `revenue_by_country(users, orders, keep_unknown)` — total amount of PAID
   orders per country (inner join on user_id). With keep_unknown=False, rows
   whose country is missing are dropped; with True they form a group named
   "unknown". Return a Series indexed by country, sorted by index, rounded to
   2 dp.
3. `sql_revenue_by_country(conn)` — the keep_unknown=True result from SQLite
   tables `users` and `orders` (COALESCE the NULL country).
4. `null_semantics()` — return a dict comparing pandas and SQLite on the
   column [NULL, NULL] and on [1, NULL, 3]:
   {"pandas_sum_all_null", "sql_sum_all_null", "pandas_count", "sql_count",
    "pandas_size", "sql_count_star", "pandas_mean", "sql_avg"}.

Examples
--------
>>> null_semantics()["pandas_sum_all_null"], null_semantics()["sql_sum_all_null"]
(0.0, None)

Constraints
-----------
- n <= 10**6 orders. Group medians must be computed in one pass, not per row.

Hints
-----
- `x == np.nan` is always False; use isna().
- groupby drops NaN keys unless dropna=False; SQL GROUP BY keeps a NULL group.
- Sum of an all-NaN group: pandas gives 0.0 (min_count=0); SQL SUM gives NULL.
- Series.count() counts non-null values like COUNT(col); len()/size is COUNT(*).

Follow-ups
----------
- Forward-fill a sensor reading per device (groupby().ffill()).
- When is dropping rows better than imputing? (Missing-not-at-random data.)
- Integer column with missing values: the nullable "Int64" dtype keeps ints.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    users = pd.read_csv(DATA / "users.csv", parse_dates=["signup_date"])
    orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"])
    return users, orders


def brute_force_clean(orders: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError("TODO")


def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError("TODO")


def revenue_by_country(users: pd.DataFrame, orders: pd.DataFrame, keep_unknown: bool) -> pd.Series:
    raise NotImplementedError("TODO")


SQL_REVENUE = """
-- TODO: write the query
"""


def sql_revenue_by_country(conn: sqlite3.Connection) -> pd.Series:
    raise NotImplementedError("TODO")


def null_semantics() -> dict:
    raise NotImplementedError("TODO")


def to_sqlite(users: pd.DataFrame, orders: pd.DataFrame) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    users.assign(signup_date=users["signup_date"].dt.strftime("%Y-%m-%d")).to_sql("users", conn, index=False)
    orders.assign(order_date=orders["order_date"].dt.strftime("%Y-%m-%d")).to_sql("orders", conn, index=False)
    return conn


def main() -> None:
    users, orders = load()
    print("missing per column:", orders.isna().sum().to_dict(), "| duplicate rows:", int(orders.duplicated().sum()))
    cleaned = clean_orders(orders)
    print("rows before/after dedup:", len(orders), len(cleaned),
          "| NaN left:", int(cleaned["amount"].isna().sum()))
    print("imputed rows:")
    print(cleaned.loc[cleaned["imputed"], ["order_id", "user_id", "amount"]].round(2).to_string(index=False))
    print("matches brute force:", cleaned.equals(brute_force_clean(orders)))
    print("countries missing:", int(users["country"].isna().sum()),
          "| users['country'] == np.nan finds:", int((users["country"] == np.nan).sum()))
    print("revenue, NaN group dropped (groupby default):")
    print(revenue_by_country(users, orders, keep_unknown=False).to_string())
    pandas_rev = revenue_by_country(users, orders, keep_unknown=True)
    with closing(to_sqlite(users, orders)) as conn:
        sql_rev = sql_revenue_by_country(conn)
    print("with unknown:", pandas_rev.to_dict())
    print("SQL GROUP BY (keeps NULL) matches:", sql_rev.to_dict() == pandas_rev.to_dict())
    for k, v in null_semantics().items():
        print(f"  {k:20s} {v}")


if __name__ == "__main__":
    main()
