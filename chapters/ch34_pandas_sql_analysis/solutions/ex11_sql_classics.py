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

Approach ladder
---------------
1. Brute force — per group: sorted(set(values), reverse=True)[n-1];
   per user: max over (date, id) tuples; streaks: walk sorted dates.
   O(n log n) overall but Python loops.
2. Optimal    — vectorised ranks: groupby().rank(method="dense",
   ascending=False) == n (O(n log n) for the per-group sort);
   sort_values + drop_duplicates(keep="last") for the latest row (O(n log n));
   gaps-and-islands: date - row_number * 1 day is constant inside a run,
   so group by that key (O(n log n) sort + O(n) grouping).
   SQL: DENSE_RANK() / ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...).
   Why move up: same bounds, one expression each, and it maps 1:1 to SQL.

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
    out = {}
    for g in sorted(df[group].unique()):
        vals = sorted({v for v in df.loc[df[group] == g, value] if not pd.isna(v)}, reverse=True)
        out[g] = vals[n - 1] if len(vals) >= n else None
    return out


def nth_highest(df: pd.DataFrame, group: str, value: str, n: int) -> dict:
    ranks = df.groupby(group)[value].rank(method="dense", ascending=False)
    hits = df.loc[ranks == n].groupby(group)[value].first()
    return {g: (hits[g].item() if g in hits.index else None) for g in sorted(df[group].unique())}


def latest_per_user(orders: pd.DataFrame) -> dict[int, int]:
    last = orders.sort_values(["user_id", "order_date", "order_id"]).drop_duplicates("user_id", keep="last")
    return dict(zip(last["user_id"].tolist(), last["order_id"].tolist()))


def brute_force_streak(sales: pd.DataFrame) -> dict[str, tuple[str, int]]:
    out = {}
    for store in sorted(sales["store"].unique()):
        days = sorted(sales.loc[sales["store"] == store, "date"].dt.date)
        best, start, length = (None, 0), days[0], 1
        for prev, cur in zip(days, days[1:] + [None]):
            if cur is not None and cur - prev == timedelta(days=1):
                length += 1
                continue
            if length > best[1]:
                best = (start.isoformat(), length)
            start, length = cur, 1
        out[store] = best
    return out


def longest_streak(sales: pd.DataFrame) -> dict[str, tuple[str, int]]:
    df = sales.sort_values(["store", "date"])
    step = pd.to_timedelta(df.groupby("store").cumcount(), unit="D")
    df = df.assign(island=df["date"] - step)
    runs = (df.groupby(["store", "island"])["date"].agg(first="min", length="size").reset_index()
            .sort_values(["store", "length", "first"], ascending=[True, False, True])
            .drop_duplicates("store"))
    return {r.store: (r.first.strftime("%Y-%m-%d"), int(r.length)) for r in runs.itertuples()}


SQL_NTH = """
SELECT g, v FROM (
    SELECT g, v, DENSE_RANK() OVER (PARTITION BY g ORDER BY v DESC) AS r
    FROM t WHERE v IS NOT NULL
) WHERE r = :n GROUP BY g
"""
SQL_LATEST = """
SELECT user_id, order_id FROM (
    SELECT user_id, order_id,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date DESC, order_id DESC) AS rn
    FROM orders
) WHERE rn = 1 ORDER BY user_id
"""
SQL_STREAK = """
WITH k AS (
    SELECT store, date,
           julianday(date) - ROW_NUMBER() OVER (PARTITION BY store ORDER BY date) AS island
    FROM sales
), runs AS (
    SELECT store, MIN(date) AS first, COUNT(*) AS length FROM k GROUP BY store, island
)
SELECT store, first, length FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY store ORDER BY length DESC, first) AS rn FROM runs
) WHERE rn = 1 ORDER BY store
"""


def sql_nth_highest(conn: sqlite3.Connection, n: int) -> dict:
    groups = [g for (g,) in conn.execute("SELECT DISTINCT g FROM t ORDER BY g")]
    found = dict(conn.execute(SQL_NTH, {"n": n}).fetchall())
    return {g: found.get(g) for g in groups}


def sql_latest_per_user(conn: sqlite3.Connection) -> dict[int, int]:
    return dict(conn.execute(SQL_LATEST).fetchall())


def sql_longest_streak(conn: sqlite3.Connection) -> dict[str, tuple[str, int]]:
    return {s: (f, n) for s, f, n in conn.execute(SQL_STREAK)}


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
