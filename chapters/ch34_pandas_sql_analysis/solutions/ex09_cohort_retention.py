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

Approach ladder
---------------
1. Brute force — for every cohort and every k, scan all orders and collect
   user_ids that match: O(C * K * n).
2. Improved   — one pass building {(cohort, k): set(user_ids)}: O(n), then
   fill the grid: O(C * K). Still Python-level loops.
3. Optimal    — vectorised: join orders to users, k = month_index(order) -
   month_index(signup) as integers, drop_duplicates on (user, k), then
   groupby([cohort, k]).user_id.nunique() + unstack: O(n) hashing, and
   divide by the cohort-size Series (index alignment does the broadcast).
   Why move up: rung 1 rescans the data C*K times; rung 3 is one grouped pass.

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
    u = users.assign(c_idx=month_index(users["signup_date"]))
    size = u.groupby("c_idx")["user_id"].nunique()
    paid = orders[orders["status"] == "paid"].merge(u[["user_id", "c_idx"]], on="user_id")
    o_idx = month_index(paid["order_date"])
    paid = paid.assign(k=o_idx - paid["c_idx"])
    last = int(month_index(orders["order_date"]).max())
    active = (paid[paid["k"] >= 0].drop_duplicates(["user_id", "k"])
              .groupby(["c_idx", "k"])["user_id"].nunique().unstack(fill_value=0))
    ks = range(0, last - int(size.index.min()) + 1)
    active = active.reindex(index=size.index, columns=ks, fill_value=0)
    rates = active.div(size, axis=0)
    observable = (np.add.outer(size.index.to_numpy(), np.array(ks)) <= last)
    rates = rates.where(observable).round(3)
    rates.insert(0, "size", size)
    rates.index = [label(i) for i in rates.index]
    rates.index.name = "cohort"
    rates.columns.name = None
    return rates


def brute_force_retention(users: pd.DataFrame, orders: pd.DataFrame) -> dict:
    cohort = {r.user_id: r.signup_date.year * 12 + r.signup_date.month for r in users.itertuples()}
    size = defaultdict(int)
    for c in cohort.values():
        size[c] += 1
    cells = defaultdict(set)
    last = max(d.year * 12 + d.month for d in orders["order_date"])
    for r in orders.itertuples():
        if r.status == "paid" and r.user_id in cohort:
            k = r.order_date.year * 12 + r.order_date.month - cohort[r.user_id]
            if k >= 0:
                cells[(cohort[r.user_id], k)].add(r.user_id)
    first = min(size)
    return {label(c): [round(len(cells[(c, k)]) / size[c], 3) if c + k <= last else None
                       for k in range(last - first + 1)] for c in sorted(size)}


SQL_RETENTION = """
WITH u AS (
    SELECT user_id, CAST(strftime('%Y', signup_date) AS INT) * 12
                    + CAST(strftime('%m', signup_date) AS INT) AS c_idx
    FROM users
), sizes AS (
    SELECT c_idx, COUNT(*) AS size FROM u GROUP BY c_idx
), act AS (
    SELECT DISTINCT u.c_idx, o.user_id,
           CAST(strftime('%Y', o.order_date) AS INT) * 12
           + CAST(strftime('%m', o.order_date) AS INT) - u.c_idx AS k
    FROM orders AS o JOIN u ON u.user_id = o.user_id
    WHERE o.status = 'paid'
)
SELECT s.c_idx, a.k, COUNT(a.user_id) AS active, s.size
FROM sizes AS s JOIN act AS a ON a.c_idx = s.c_idx
WHERE a.k >= 0
GROUP BY s.c_idx, a.k ORDER BY s.c_idx, a.k
"""


def sql_retention(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql_query(SQL_RETENTION, conn)
    df.insert(0, "cohort", [label(i) for i in df.pop("c_idx")])
    return df


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
