"""
Exercise 11 — Classic Analytical Questions: Nth Highest, Latest, Streaks  [Tier: ◆ Extended]
Chapter 34 · Pattern: rank / dedup-by-rank / gaps-and-islands · Target time: 30 min

Problem
-------
Answer each in pandas AND SQLite (functions prefixed sql_).
1. `nth_highest(df, group, value, n)` — per group, the n-th highest DISTINCT
   value (ties share a rank, like DENSE_RANK); None for a group with fewer
   than n distinct values. Return {group: value-or-None} sorted by group.
   NaN values are ignored.
2. `latest_per_user(orders)` — per user_id, the order_id of their latest
   order_date; on equal dates take the larger order_id. Returns
   {user_id: order_id}. Exact duplicate rows must not matter.
3. `longest_streak(sales)` — per store, the longest run of CONSECUTIVE
   calendar days that have a row: {store: (first ISO date, length)}; the
   earliest run on ties.

Examples
--------
>>> nth_highest(pd.DataFrame({"g": ["a", "a", "a"], "v": [5, 5, 3]}), "g", "v", 2)
{'a': 3}

Constraints
-----------
- n rows; dates unique per store in (3).

Hints
-----
- rank methods: "first" = ROW_NUMBER, "min" = RANK, "dense" = DENSE_RANK.
- `LIMIT 1 OFFSET n-1` on DISTINCT values only answers ONE group.
- Islands: subtract the cumcount (0, 1, 2, ...) in days from each date. Dates
  must be unique per key: dedupe first, or use DENSE_RANK in SQL, else a
  repeated date splits a run.
- SQLite: julianday(date) - ROW_NUMBER() OVER (PARTITION BY store ORDER BY date).

Follow-ups
----------
- "Second highest salary" when the table has one row: return NULL, not
  an empty result (wrap in a scalar subquery).
- Top-3 per group INCLUDING ties: dense rank <= 3 (may return > 3 rows).
- Streaks of users logging in on consecutive days (same island trick).
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import timedelta
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)


def brute_force_nth_highest(df: pd.DataFrame, group: str, value: str, n: int) -> dict:
    raise NotImplementedError("TODO")


def nth_highest(df: pd.DataFrame, group: str, value: str, n: int) -> dict:
    raise NotImplementedError("TODO")


def latest_per_user(orders: pd.DataFrame) -> dict[int, int]:
    raise NotImplementedError("TODO")


def brute_force_streak(sales: pd.DataFrame) -> dict[str, tuple[str, int]]:
    raise NotImplementedError("TODO")


def longest_streak(sales: pd.DataFrame) -> dict[str, tuple[str, int]]:
    raise NotImplementedError("TODO")


SQL_NTH = """
-- TODO: write the query
"""
SQL_LATEST = """
-- TODO: write the query
"""
SQL_STREAK = """
-- TODO: write the query
"""


def sql_nth_highest(conn: sqlite3.Connection, n: int) -> dict:
    raise NotImplementedError("TODO")


def sql_latest_per_user(conn: sqlite3.Connection) -> dict[int, int]:
    raise NotImplementedError("TODO")


def sql_longest_streak(conn: sqlite3.Connection) -> dict[str, tuple[str, int]]:
    raise NotImplementedError("TODO")


def main() -> None:
    users = pd.read_csv(DATA / "users.csv")
    orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"])
    sales = pd.read_csv(DATA / "daily_sales.csv", parse_dates=["date"])

    paid = orders[orders["status"] == "paid"].merge(users, on="user_id")
    paid = paid.assign(country=paid["country"].fillna("unknown"))
    t = paid[["country", "amount"]].rename(columns={"country": "g", "amount": "v"})
    second = nth_highest(t, "g", "v", 2)
    print("2nd highest paid order per country:", second)
    print("brute force agrees:", second == brute_force_nth_highest(t, "g", "v", 2))
    ties = pd.DataFrame({"g": ["a", "a", "a", "b"], "v": [9.0, 9.0, 4.0, 7.0]})
    print("ties [9, 9, 4] / single [7]:", nth_highest(ties, "g", "v", 2))

    latest = latest_per_user(orders)
    print("latest order of users 1-5:", {u: latest[u] for u in range(1, 6)})
    streak = longest_streak(sales)
    print("longest daily streak:", streak, "| brute force agrees:", streak == brute_force_streak(sales))

    with closing(sqlite3.connect(":memory:")) as conn:
        t.to_sql("t", conn, index=False)
        orders.assign(order_date=orders["order_date"].dt.strftime("%Y-%m-%d")).to_sql("orders", conn, index=False)
        sales.assign(date=sales["date"].dt.strftime("%Y-%m-%d")).to_sql("sales", conn, index=False)
        print("SQL DENSE_RANK agrees:", sql_nth_highest(conn, 2) == second)
        print("SQL ROW_NUMBER agrees:", sql_latest_per_user(conn) == latest)
        print("SQL islands agree    :", sql_longest_streak(conn) == streak)


if __name__ == "__main__":
    main()
