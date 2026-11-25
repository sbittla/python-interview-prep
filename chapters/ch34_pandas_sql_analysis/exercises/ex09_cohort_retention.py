"""
Exercise 09 — Monthly Cohort Retention Matrix                        [Tier: ★ Core]
Chapter 34 · Pattern: cohort key + period offset + pivot · Target time: 30 min

Problem
-------
A user's cohort is their signup month ("YYYY-MM"). A user is ACTIVE in month
offset k (k = 0 is the signup month) if they have at least one PAID order in
calendar month cohort + k. Using users.csv and orders.csv:
1. `retention(users, orders)` — DataFrame indexed by cohort (sorted), with a
   column `size` (number of users who signed up, INCLUDING those who never
   ordered) and columns 0, 1, 2, ... (int) holding active_users / size,
   rounded to 3 dp. A cell is NaN when cohort + k is after the last month in
   the data (not observable yet); it is 0.0 when observable but nobody was
   active. Orders from user_ids missing in users are ignored.
2. `brute_force_retention(...)` — same numbers via sets and loops.
3. `sql_retention(conn)` — long table (cohort, k, active, size) from SQLite
   with CTEs, for cross-checking.

Examples
--------
>>> retention(users, orders).loc["2026-01", "size"]
8

Constraints
-----------
- U users, n orders, C cohorts, K offsets; output is C x K.

Hints
-----
- month index = year * 12 + month; subtracting gives k as a plain int (no
  Period-offset objects).
- Cohort size comes from users, not from orders: a user who never orders
  still lowers retention.
- Count DISTINCT users per cell: two orders in one month are one active user.
- Mask cells where cohort_index + k > last observed month index.

Follow-ups
----------
- Revenue retention instead of user retention: sum amount, divide by k = 0.
- Weekly cohorts; rolling (any-later-month) vs classic (exact-month) retention.
- Orders dated BEFORE signup (bad data): k < 0 — drop and count them.
"""
from __future__ import annotations

import sqlite3
from collections import defaultdict
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


def month_index(s: pd.Series) -> pd.Series:
    return s.dt.year * 12 + s.dt.month


def label(idx: int) -> str:
    y, m = divmod(idx - 1, 12)
    return f"{y:04d}-{m + 1:02d}"


def retention(users: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError("TODO")


def brute_force_retention(users: pd.DataFrame, orders: pd.DataFrame) -> dict:
    raise NotImplementedError("TODO")


SQL_RETENTION = """
-- TODO: write the query
"""


def sql_retention(conn: sqlite3.Connection) -> pd.DataFrame:
    raise NotImplementedError("TODO")


def to_sqlite(users: pd.DataFrame, orders: pd.DataFrame) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    users.assign(signup_date=users["signup_date"].dt.strftime("%Y-%m-%d")).to_sql("users", conn, index=False)
    orders.assign(order_date=orders["order_date"].dt.strftime("%Y-%m-%d")).to_sql("orders", conn, index=False)
    return conn


def main() -> None:
    users, orders = load()
    ret = retention(users, orders)
    print(ret.to_string())
    as_lists = {c: [None if pd.isna(v) else v for v in row[1:]] for c, row in zip(ret.index, ret.values.tolist())}
    print("matches brute force:", as_lists == brute_force_retention(users, orders))
    with closing(to_sqlite(users, orders)) as conn:
        long = sql_retention(conn)
    long["rate"] = (long["active"] / long["size"]).round(3)
    ok = all(ret.loc[r.cohort, r.k] == r.rate for r in long.itertuples())
    print("SQL long table:", len(long), "non-empty cells; all match:", ok)
    never = sorted(set(users["user_id"]) - set(orders.loc[orders["status"] == "paid", "user_id"]))
    print("users with no paid order (still in cohort size):", never)


if __name__ == "__main__":
    main()
