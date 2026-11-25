"""
Exercise 04 — Country Scorecard: groupby, Named Aggregation, transform  [Tier: ★ Core]
Chapter 34 · Pattern: split-apply-combine; transform = SQL window SUM() OVER · Target time: 20 min

Problem
-------
Join PAID orders (drop exact duplicate rows first; NaN amounts count as an
order but add nothing to revenue) to users on user_id; a missing country is
"unknown".
1. `country_summary(users, orders)` — one row per country with columns
   country, revenue (sum, 2 dp), orders (number of paid orders), buyers
   (distinct users), aov (revenue / orders with a non-null amount, 2 dp).
   Sort by revenue descending, then country. Fresh index.
2. `user_share(users, orders)` — one row per (country, user_id) with columns
   country, user_id, revenue, share = user revenue / country revenue (3 dp).
   Sort by country, then share descending, then user_id.
3. `brute_force_summary(...)` — the same table as (1) using dict loops.
4. `sql_country_summary(conn)` and `sql_user_share(conn)` — the same tables
   from SQLite (GROUP BY and SUM(...) OVER (PARTITION BY ...)).

Examples
--------
>>> country_summary(users, orders).iloc[0]["country"]
'US'

Constraints
-----------
- n <= 10**6 orders, g groups. Aim for O(n) work plus O(g log g) for sorting.

Approach ladder
---------------
1. Brute force — dict-of-lists keyed by country, then sum/len/set per key:
   O(n) time, O(n) space, all in Python objects.
2. Improved   — groupby(...).apply(lambda g: pd.Series({...})): O(n) but calls
   a Python function per group and builds a Series per group (slow for large g).
3. Optimal    — groupby(...).agg(revenue=("amount", "sum"), ...) named
   aggregation: one hash-grouped pass in C, O(n) + O(g log g) to sort group
   keys; transform("sum") broadcasts each group total back to its rows (same
   length as the input), which is exactly SQL's SUM(x) OVER (PARTITION BY k).
   Why move up: same big-O, but rung 3 is vectorised and returns flat columns.

Hints
-----
- Named aggregation: .agg(new_col=("source_col", "func")).
- "count" counts non-null values; "size" counts rows.
- transform returns one value per input ROW; agg returns one per GROUP.
- Sort with a tie-breaker so equal revenues have a deterministic order.

Follow-ups
----------
- Top-2 buyers per country with ties (→ ex11, DENSE_RANK).
- Share within country AND month: group by two keys.
- Why does `groupby(...).mean()` on the whole frame fail on string columns in
  pandas 2+? (numeric_only now defaults to False.)
"""
from __future__ import annotations

import sqlite3
from collections import defaultdict
from contextlib import closing
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    users = pd.read_csv(DATA / "users.csv", parse_dates=["signup_date"])
    orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"])
    return users, orders


def paid_with_country(users: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    paid = orders.drop_duplicates().query("status == 'paid'")
    out = paid.merge(users[["user_id", "country"]], on="user_id", how="inner")
    return out.assign(country=out["country"].fillna("unknown"))


def country_summary(users: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    df = paid_with_country(users, orders)
    g = df.groupby("country", as_index=False).agg(
        revenue=("amount", "sum"),
        orders=("order_id", "size"),
        priced=("amount", "count"),
        buyers=("user_id", "nunique"),
    )
    g["aov"] = (g["revenue"] / g["priced"]).round(2)
    g["revenue"] = g["revenue"].round(2)
    g = g.drop(columns="priced")
    return g.sort_values(["revenue", "country"], ascending=[False, True]).reset_index(drop=True)


def user_share(users: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    df = paid_with_country(users, orders)
    per_user = df.groupby(["country", "user_id"], as_index=False)["amount"].sum()
    per_user = per_user.rename(columns={"amount": "revenue"})
    country_total = per_user.groupby("country")["revenue"].transform("sum")
    per_user["share"] = (per_user["revenue"] / country_total).round(3)
    per_user["revenue"] = per_user["revenue"].round(2)
    return per_user.sort_values(["country", "share", "user_id"],
                                ascending=[True, False, True]).reset_index(drop=True)


def brute_force_summary(users: pd.DataFrame, orders: pd.DataFrame) -> list[tuple]:
    country_of = {u: ("unknown" if pd.isna(c) else c) for u, c in zip(users["user_id"], users["country"])}
    seen, groups = set(), defaultdict(list)
    for row in orders.itertuples(index=False):
        key = tuple("nan" if pd.isna(v) else v for v in row)
        if key in seen or row.status != "paid" or row.user_id not in country_of:
            continue
        seen.add(key)
        groups[country_of[row.user_id]].append(row)
    out = []
    for country, rows in groups.items():
        amounts = [r.amount for r in rows if not pd.isna(r.amount)]
        revenue = sum(amounts)
        out.append((country, round(revenue, 2), len(rows), len({r.user_id for r in rows}),
                    round(revenue / len(amounts), 2)))
    return sorted(out, key=lambda t: (-t[1], t[0]))


SQL_SUMMARY = """
WITH paid AS (
    SELECT DISTINCT o.order_id, o.user_id, o.order_date, o.amount, o.status,
           COALESCE(u.country, 'unknown') AS country
    FROM orders AS o JOIN users AS u ON u.user_id = o.user_id
    WHERE o.status = 'paid'
)
SELECT country, ROUND(TOTAL(amount), 2) AS revenue, COUNT(*) AS orders,
       COUNT(DISTINCT user_id) AS buyers, ROUND(TOTAL(amount) / COUNT(amount), 2) AS aov
FROM paid GROUP BY country ORDER BY TOTAL(amount) DESC, country
"""

SQL_SHARE = """
WITH paid AS (
    SELECT DISTINCT o.order_id, o.user_id, o.amount, COALESCE(u.country, 'unknown') AS country
    FROM orders AS o JOIN users AS u ON u.user_id = o.user_id
    WHERE o.status = 'paid'
), per_user AS (
    SELECT country, user_id, TOTAL(amount) AS revenue FROM paid GROUP BY country, user_id
)
SELECT country, user_id, ROUND(revenue, 2) AS revenue,
       ROUND(revenue / SUM(revenue) OVER (PARTITION BY country), 3) AS share
FROM per_user ORDER BY country, share DESC, user_id
"""


def sql_country_summary(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(SQL_SUMMARY, conn)


def sql_user_share(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(SQL_SHARE, conn)


def to_sqlite(users: pd.DataFrame, orders: pd.DataFrame) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    users.assign(signup_date=users["signup_date"].dt.strftime("%Y-%m-%d")).to_sql("users", conn, index=False)
    orders.assign(order_date=orders["order_date"].dt.strftime("%Y-%m-%d")).to_sql("orders", conn, index=False)
    return conn


def main() -> None:
    users, orders = load()
    summary = country_summary(users, orders)
    print(summary.to_string(index=False))
    brute = brute_force_summary(users, orders)
    print("brute force matches:", brute == list(summary.itertuples(index=False, name=None)))
    share = user_share(users, orders)
    print("top user per country:")
    print(share.groupby("country").head(1).to_string(index=False))
    print("shares sum to 1 per country:",
          share.groupby("country")["share"].sum().round(2).eq(1.0).all())
    with closing(to_sqlite(users, orders)) as conn:
        sql_sum, sql_share = sql_country_summary(conn), sql_user_share(conn)
    print("SQL summary matches:", sql_sum.equals(summary))
    print("SQL share matches  :", sql_share.equals(share))
    totals = share.groupby("country")["revenue"].transform("sum")
    print("agg -> one row per group:", len(summary), "| transform -> one value per input row:",
          len(totals), "of", len(share))


if __name__ == "__main__":
    main()
