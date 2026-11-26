"""
Exercise 05 — Joins: Inner, Left, Anti, and Duplicate-Key Traps      [Tier: ★ Core]
Chapter 34 · Pattern: merge(how=, indicator=, validate=) = SQL JOIN · Target time: 20 min

Problem
-------
1. `orders_per_user(users, orders)` — every user (LEFT join) with n_orders =
   number of distinct order_ids (0 for users with none). Columns user_id,
   n_orders; sorted by user_id.
2. `orphan_orders(orders, users)` — ANTI join: order_ids whose user_id is not
   in users, sorted ascending.
3. `checked_lookup(orders, lookup)` — attach lookup columns to orders on
   user_id, but raise pandas.errors.MergeError if `lookup` has a duplicate
   user_id (it would silently multiply order rows).
4. `join_row_count(left_keys, right_keys)` — how many rows an inner join on
   these key lists produces (sum over keys of left_count * right_count),
   computed without building the join.
5. SQL versions `sql_orders_per_user(conn)` and `sql_orphan_orders(conn)`.

Examples
--------
>>> join_row_count([1, 1, 2], [1, 1, 1, 3])
6

Constraints
-----------
- n, m <= 10**6 rows.

Approach ladder
---------------
1. Brute force — nested loops over both tables: O(n * m).
2. Improved   — sort both by key and merge-walk: O(n log n + m log m)
   (a sort-merge join).
3. Optimal    — hash join: build a hash table on one side, probe with the
   other: O(n + m + output). pandas merge factorises keys with hashing.
   Why move up: O(n*m) is 10**12 at a million rows each.
   Output size can still be quadratic: duplicate keys multiply (rule 4).

Hints
-----
- merge(..., how="left", indicator=True) adds `_merge` in {"both",
  "left_only", "right_only"}: anti join = keep "left_only".
- `validate="many_to_one"` checks the right side's keys are unique.
- After a left join, count a real column (`order_id`), not rows: unmatched
  users have one row with NaN order_id.
- pandas joins NaN keys to NaN keys; SQL NULL = NULL is never true.

Follow-ups
----------
- Semi join (users who ordered at least once): users[users.user_id.isin(...)].
- concat vs merge: concat stacks frames (UNION ALL); merge matches keys (JOIN).
- Joining on a range ("price valid between from/to") → merge_asof or SQL
  BETWEEN join.
"""
from __future__ import annotations

import sqlite3
from collections import Counter
from contextlib import closing
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.errors import MergeError

DATA = Path(__file__).resolve().parent.parent / "data"
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    return pd.read_csv(DATA / "users.csv"), pd.read_csv(DATA / "orders.csv")


def orders_per_user(users: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    joined = users[["user_id"]].merge(orders[["order_id", "user_id"]], on="user_id", how="left")
    counts = joined.groupby("user_id", as_index=False).agg(n_orders=("order_id", "nunique"))
    return counts.sort_values("user_id").reset_index(drop=True)


def orphan_orders(orders: pd.DataFrame, users: pd.DataFrame) -> list[int]:
    tagged = orders.merge(users[["user_id"]], on="user_id", how="left", indicator=True)
    return sorted(tagged.loc[tagged["_merge"] == "left_only", "order_id"].unique().tolist())


def checked_lookup(orders: pd.DataFrame, lookup: pd.DataFrame) -> pd.DataFrame:
    return orders.merge(lookup, on="user_id", how="left", validate="many_to_one")


def brute_force_join_count(left_keys: list, right_keys: list) -> int:
    return sum(1 for a in left_keys for b in right_keys if a == b)


def join_row_count(left_keys: list, right_keys: list) -> int:
    right = Counter(right_keys)
    return sum(n * right[k] for k, n in Counter(left_keys).items())


SQL_PER_USER = """
SELECT u.user_id, COUNT(DISTINCT o.order_id) AS n_orders
FROM users AS u LEFT JOIN orders AS o ON o.user_id = u.user_id
GROUP BY u.user_id ORDER BY u.user_id
"""
SQL_ORPHANS = """
SELECT DISTINCT o.order_id
FROM orders AS o LEFT JOIN users AS u ON u.user_id = o.user_id
WHERE u.user_id IS NULL ORDER BY o.order_id
"""


def sql_orders_per_user(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(SQL_PER_USER, conn)


def sql_orphan_orders(conn: sqlite3.Connection) -> list[int]:
    return [r[0] for r in conn.execute(SQL_ORPHANS)]


def main() -> None:
    users, orders = load()
    per_user = orders_per_user(users, orders)
    print("users:", len(users), "| result rows:", len(per_user),
          "| users with 0 orders:", per_user.loc[per_user["n_orders"] == 0, "user_id"].tolist())
    print("orphan orders (anti join):", orphan_orders(orders, users))
    with closing(sqlite3.connect(":memory:")) as conn:
        users.to_sql("users", conn, index=False)
        orders.to_sql("orders", conn, index=False)
        print("SQL per-user matches:", sql_orders_per_user(conn).equals(per_user))
        print("SQL orphans:", sql_orphan_orders(conn))
    inner = orders.merge(users, on="user_id")
    left = orders.merge(users, on="user_id", how="left")
    print("orders:", len(orders), "| inner join rows:", len(inner), "| left join rows:", len(left))

    dup_lookup = pd.DataFrame({"user_id": [2, 2, 4], "tier": ["gold", "silver", "gold"]})
    exploded = orders.merge(dup_lookup, on="user_id")
    print("user 2 orders:", int((orders["user_id"] == 2).sum()),
          "| rows after joining a lookup with user 2 twice:", int((exploded["user_id"] == 2).sum()))
    try:
        checked_lookup(orders, dup_lookup)
    except MergeError as exc:
        print("validate='many_to_one' ->", type(exc).__name__ + ":", str(exc).split(";")[0][:60])
    print("join_row_count([1,1,2],[1,1,1,3]) =", join_row_count([1, 1, 2], [1, 1, 1, 3]),
          "| brute:", brute_force_join_count([1, 1, 2], [1, 1, 1, 3]))

    a = pd.DataFrame({"k": ["x", np.nan], "a": [1, 2]})
    b = pd.DataFrame({"k": ["x", np.nan], "b": [10, 20]})
    print("pandas joins NaN to NaN:", len(a.merge(b, on="k")), "rows")
    with closing(sqlite3.connect(":memory:")) as conn:
        a.to_sql("a", conn, index=False)
        b.to_sql("b", conn, index=False)
        n = conn.execute("SELECT COUNT(*) FROM a JOIN b ON a.k = b.k").fetchone()[0]
    print("SQL joins NULL to NULL:", n, "row(s) (only 'x')")
    stacked = pd.concat([orders.head(2), orders.tail(2)], keys=["first", "last"])
    print("concat keys:", sorted(set(stacked.index.get_level_values(0))), "| rows:", len(stacked))


if __name__ == "__main__":
    main()
