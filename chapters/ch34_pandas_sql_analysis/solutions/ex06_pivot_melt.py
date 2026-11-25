"""
Exercise 06 — Pivot Tables and Melt (Long <-> Wide)                  [Tier: ◆ Extended]
Chapter 34 · Pattern: pivot_table = SQL conditional aggregation · Target time: 20 min

Problem
-------
1. `monthly_wide(users, orders)` — paid revenue (exact duplicate rows
   dropped) by country (rows, missing -> "unknown") and month "YYYY-MM"
   (columns), 0.0 where a country has no paid orders that month, plus a
   final "total" column. Rows sorted by country, month columns ascending,
   values rounded to 2 dp.
2. `to_long(wide)` — melt the month columns (not "total") back to long
   format: columns country, month, revenue; drop zero rows; sort by country,
   month; fresh index.
3. `sql_monthly_long(conn)` — the same long table from SQLite
   (GROUP BY country, month), for cross-checking.
4. `pivot_or_error(df)` — try df.pivot(index="k", columns="c", values="v");
   return "ValueError" if pandas refuses because an (index, column) pair
   repeats, else "ok".

Examples
--------
>>> pivot_or_error(pd.DataFrame({"k": [1, 1], "c": ["a", "a"], "v": [1, 2]}))
'ValueError'

Constraints
-----------
- n orders, r countries, c months: output is r x c cells.

Approach ladder
---------------
1. Brute force — nested dict {country: {month: total}}, then fill a grid by
   looping over every (country, month): O(n + r*c).
2. Optimal    — pivot_table(index, columns, values, aggfunc="sum",
   fill_value=0): one grouped pass + an unstack, O(n + r*c); melt reverses
   it in O(r*c). SQL needs one SUM(CASE WHEN month = ... ) per column, so
   pivoting in SQL means knowing the columns up front.
   Why move up: pivot_table also handles duplicates (it aggregates) and
   missing cells (fill_value) in one call.

Hints
-----
- dt.strftime("%Y-%m") builds a sortable month label.
- pivot reshapes only; pivot_table aggregates (default aggfunc is "mean"!).
- melt(id_vars=[...], value_vars=[...], var_name=..., value_name=...).
- columns.name is left over after pivot_table; rename_axis(columns=None).

Follow-ups
----------
- Add a "total" ROW (margins=True or df.loc["total"] = df.sum()).
- stack/unstack: the index-based cousins of melt/pivot.
- Pivot when months are unknown in SQL: query long, pivot in pandas.
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
    users = pd.read_csv(DATA / "users.csv")
    orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"])
    return users, orders


def paid_rows(users: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    paid = orders.drop_duplicates().query("status == 'paid'")
    df = paid.merge(users[["user_id", "country"]], on="user_id")
    return df.assign(country=df["country"].fillna("unknown"),
                     month=df["order_date"].dt.strftime("%Y-%m"))


def monthly_wide(users: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    df = paid_rows(users, orders)
    wide = df.pivot_table(index="country", columns="month", values="amount",
                          aggfunc="sum", fill_value=0.0)
    wide = wide.rename_axis(index=None, columns=None).sort_index()
    wide = wide[sorted(wide.columns)]
    wide["total"] = wide.sum(axis=1)
    return wide.round(2)


def brute_force_wide(users: pd.DataFrame, orders: pd.DataFrame) -> dict:
    df = paid_rows(users, orders)
    grid: dict = defaultdict(lambda: defaultdict(float))
    for country, month, amount in zip(df["country"], df["month"], df["amount"]):
        grid[country][month] += 0.0 if pd.isna(amount) else amount
    months = sorted({m for row in grid.values() for m in row})
    return {c: [round(grid[c][m], 2) for m in months] for c in sorted(grid)}


def to_long(wide: pd.DataFrame) -> pd.DataFrame:
    months = [c for c in wide.columns if c != "total"]
    long = wide.rename_axis("country").reset_index().melt(
        id_vars="country", value_vars=months, var_name="month", value_name="revenue")
    long = long[long["revenue"] != 0]
    return long.sort_values(["country", "month"]).reset_index(drop=True)


SQL_LONG = """
SELECT COALESCE(u.country, 'unknown') AS country, strftime('%Y-%m', o.order_date) AS month,
       ROUND(TOTAL(o.amount), 2) AS revenue
FROM (SELECT DISTINCT * FROM orders WHERE status = 'paid') AS o
JOIN users AS u ON u.user_id = o.user_id
GROUP BY 1, 2 HAVING TOTAL(o.amount) <> 0 ORDER BY 1, 2
"""
SQL_WIDE_TWO_MONTHS = """
SELECT COALESCE(u.country, 'unknown') AS country,
       ROUND(TOTAL(CASE WHEN strftime('%Y-%m', o.order_date) = '2026-01' THEN o.amount END), 2) AS jan,
       ROUND(TOTAL(CASE WHEN strftime('%Y-%m', o.order_date) = '2026-02' THEN o.amount END), 2) AS feb
FROM (SELECT DISTINCT * FROM orders WHERE status = 'paid') AS o
JOIN users AS u ON u.user_id = o.user_id
GROUP BY 1 ORDER BY 1
"""


def sql_monthly_long(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(SQL_LONG, conn)


def pivot_or_error(df: pd.DataFrame) -> str:
    try:
        df.pivot(index="k", columns="c", values="v")
    except ValueError:
        return "ValueError"
    return "ok"


def to_sqlite(users: pd.DataFrame, orders: pd.DataFrame) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    users.to_sql("users", conn, index=False)
    orders.assign(order_date=orders["order_date"].dt.strftime("%Y-%m-%d")).to_sql("orders", conn, index=False)
    return conn


def main() -> None:
    users, orders = load()
    wide = monthly_wide(users, orders)
    print(wide.to_string())
    print("matches brute force:", brute_force_wide(users, orders)
          == {c: row[:-1] for c, row in zip(wide.index, wide.values.tolist())})
    long = to_long(wide)
    print("long rows:", len(long), "| first three:")
    print(long.head(3).to_string(index=False))
    with closing(to_sqlite(users, orders)) as conn:
        sql_long = sql_monthly_long(conn)
        two = pd.read_sql_query(SQL_WIDE_TWO_MONTHS, conn)
    print("SQL long matches melt:", sql_long.equals(long))
    print("SQL CASE-WHEN pivot matches Jan/Feb columns:",
          two["jan"].tolist() == wide["2026-01"].tolist() and two["feb"].tolist() == wide["2026-02"].tolist())
    dup = pd.DataFrame({"k": [1, 1, 2], "c": ["a", "a", "a"], "v": [1, 2, 3]})
    print("pivot with a repeated (k, c):", pivot_or_error(dup),
          "| pivot_table default aggfunc:", dup.pivot_table(index="k", columns="c", values="v")["a"].tolist())


if __name__ == "__main__":
    main()
