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

Approach ladder
---------------
1. Brute force — for each NaN row, filter the frame to that user and take the
   median: O(n * m) for m missing rows (O(n^2) worst case).
2. Optimal    — groupby("user_id")["amount"].transform("median") gives every
   row its group's median in one O(n) hash-grouped pass (+ O(n log n) worst
   case for the medians); fillna with it, then with the global median.
   Why move up: one vectorised pass instead of a filter per missing value.

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
    out = orders.drop_duplicates().copy()
    global_median = out["amount"].median()
    filled = []
    for _, row in out.iterrows():
        if pd.isna(row["amount"]):
            same = out.loc[out["user_id"] == row["user_id"], "amount"].dropna()
            filled.append(same.median() if len(same) else global_median)
        else:
            filled.append(row["amount"])
    out["imputed"] = out["amount"].isna()
    out["amount"] = filled
    return out.sort_values("order_id").reset_index(drop=True)


def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    out = orders.drop_duplicates()
    user_median = out.groupby("user_id")["amount"].transform("median")
    out = out.assign(
        imputed=out["amount"].isna(),
        amount=out["amount"].fillna(user_median).fillna(out["amount"].median()),
    )
    return out.sort_values("order_id").reset_index(drop=True)


def revenue_by_country(users: pd.DataFrame, orders: pd.DataFrame, keep_unknown: bool) -> pd.Series:
    paid = orders[orders["status"] == "paid"].merge(users[["user_id", "country"]], on="user_id")
    rev = paid.groupby("country", dropna=not keep_unknown)["amount"].sum()
    if keep_unknown:
        rev.index = rev.index.fillna("unknown")
    return rev.sort_index().round(2)


SQL_REVENUE = """
SELECT COALESCE(u.country, 'unknown') AS country, ROUND(SUM(o.amount), 2) AS amount
FROM orders AS o JOIN users AS u ON u.user_id = o.user_id
WHERE o.status = 'paid'
GROUP BY u.country
ORDER BY country
"""


def sql_revenue_by_country(conn: sqlite3.Connection) -> pd.Series:
    return pd.read_sql_query(SQL_REVENUE, conn, index_col="country")["amount"]


def null_semantics() -> dict:
    all_null = pd.Series([np.nan, np.nan])
    some = pd.Series([1.0, np.nan, 3.0])
    with closing(sqlite3.connect(":memory:")) as conn:
        conn.execute("CREATE TABLE a (v REAL)")
        conn.executemany("INSERT INTO a VALUES (?)", [(None,), (None,)])
        conn.execute("CREATE TABLE b (v REAL)")
        conn.executemany("INSERT INTO b VALUES (?)", [(1.0,), (None,), (3.0,)])
        sql_sum = conn.execute("SELECT SUM(v) FROM a").fetchone()[0]
        cnt, star, avg = conn.execute("SELECT COUNT(v), COUNT(*), AVG(v) FROM b").fetchone()
    return {
        "pandas_sum_all_null": float(all_null.sum()), "sql_sum_all_null": sql_sum,
        "pandas_count": int(some.count()), "sql_count": cnt,
        "pandas_size": int(some.size), "sql_count_star": star,
        "pandas_mean": float(some.mean()), "sql_avg": avg,
    }


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
