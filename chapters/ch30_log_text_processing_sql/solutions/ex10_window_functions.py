"""
Exercise 10 — Window Functions: Top-N per Group, Ranks, Running Totals   [Tier: ★ Core]
Chapter 30 · Pattern: ROW_NUMBER/RANK/DENSE_RANK, SUM() OVER, LAG · Target time: 30 min

Problem
-------
Table sales(id, region, day, amount); several sales may share a day. Write

1. `top_n_per_region(conn, n)` -> (region, day, amount) for the n largest sales of each
   region (ties broken by id), ordered by region, then rank;
2. `rank_styles(conn, region)` -> (amount, row_number, rank, dense_rank) by amount desc;
3. `running_totals(conn)` -> (region, id, day, amount, running) where `running` is the
   cumulative sum within the region in (day, id) order — exactly one new row per step;
4. `daily_change(conn)` -> (region, day, total, change vs previous day or None);
5. `top_n_python(rows, n)` -> the same as (1) without SQL, for cross-checking.

Examples
--------
>>> conn = make_db()
>>> top_n_per_region(conn, 1)
[('east', '2025-03-01', 120), ('north', '2025-03-01', 70), ('west', '2025-03-02', 90)]

Constraints
-----------
- Window functions need SQLite 3.25.0+ (2018); the venv runs 3.50.4. Check with
  `sqlite3.sqlite_version` (the library), not `sqlite3.version` (the old module version).

Approach ladder (top-N per group)
---------------------------------
1. Python: sort rows by (region, -amount, id), `itertools.groupby` on region, keep the
   first n of each group: O(r log r).
2. SQL without windows: keep a row if fewer than n rows of its region beat it
   (correlated COUNT subquery): O(r^2) without an index — the pre-2018 answer.
3. `ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC, id)` in a CTE, then
   `WHERE rn <= n`: one sort, O(r log r). Why move up: one pass, ties handled explicitly,
   and n is a parameter, not a self-join.

Hints
-----
- A window function cannot appear in WHERE (it is computed after WHERE): wrap it in a CTE
  or subquery and filter outside.
- With ORDER BY and no frame, the default frame is RANGE BETWEEN UNBOUNDED PRECEDING AND
  CURRENT ROW, which includes every *peer* (equal ORDER BY value): two sales on the same
  day get the same running total. Write `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`
  or make the ORDER BY unique.
- ROW_NUMBER never ties; RANK leaves gaps after ties (1, 1, 3); DENSE_RANK does not (1, 1, 2).

Edge cases
----------
- Region with fewer than n rows (all of them returned), ties at the n-th place (ROW_NUMBER
  cuts, RANK keeps both), n = 0 (empty), first day of a region (LAG is NULL -> None).

Follow-ups
----------
- "Top N with ties": use RANK() or DENSE_RANK() <= n and say which one you mean.
- 3-row moving average: `AVG(amount) OVER (... ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`.
- Percent of region total: `amount * 1.0 / SUM(amount) OVER (PARTITION BY region)`.
"""
from __future__ import annotations

import itertools
import sqlite3

SALES = [  # id, region, day, amount
    (1, "east", "2025-03-01", 120), (2, "east", "2025-03-02", 80),
    (3, "east", "2025-03-02", 40), (4, "east", "2025-03-03", 120),
    (5, "east", "2025-03-04", 60), (6, "west", "2025-03-01", 50),
    (7, "west", "2025-03-02", 90), (8, "west", "2025-03-03", 90),
    (9, "west", "2025-03-04", 30), (10, "north", "2025-03-01", 70),
]


def make_db(rows: list[tuple] = SALES) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE sales (id INTEGER PRIMARY KEY, region TEXT, day TEXT, amount INTEGER)")
    conn.executemany("INSERT INTO sales VALUES (?, ?, ?, ?)", rows)
    conn.commit()
    return conn


def top_n_per_region(conn: sqlite3.Connection, n: int) -> list[tuple]:
    return conn.execute("""
        WITH ranked AS (
            SELECT region, day, amount,
                   ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC, id) AS rn
            FROM sales
        )
        SELECT region, day, amount FROM ranked
        WHERE rn <= ?
        ORDER BY region, rn""", (n,)).fetchall()


def top_n_correlated(conn: sqlite3.Connection, n: int) -> list[tuple]:
    """Rung 2: a row survives if fewer than n rows of its region beat it."""
    return conn.execute("""
        SELECT region, day, amount FROM sales s
        WHERE (SELECT COUNT(*) FROM sales b
               WHERE b.region = s.region
                 AND (b.amount > s.amount OR (b.amount = s.amount AND b.id < s.id))) < ?
        ORDER BY region, amount DESC, id""", (n,)).fetchall()


def top_n_python(rows: list[tuple], n: int) -> list[tuple]:
    ordered = sorted(rows, key=lambda r: (r[1], -r[3], r[0]))
    return [(region, day, amount)
            for _, group in itertools.groupby(ordered, key=lambda r: r[1])
            for _, region, day, amount in itertools.islice(group, n)]


def rank_styles(conn: sqlite3.Connection, region: str) -> list[tuple]:
    return conn.execute("""
        SELECT amount,
               ROW_NUMBER() OVER (ORDER BY amount DESC, id),   -- unique order: no ties
               RANK() OVER w, DENSE_RANK() OVER w
        FROM sales WHERE region = ?
        WINDOW w AS (ORDER BY amount DESC)
        ORDER BY amount DESC, id""", (region,)).fetchall()


def running_totals(conn: sqlite3.Connection) -> list[tuple]:
    return conn.execute("""
        SELECT region, id, day, amount,
               SUM(amount) OVER (PARTITION BY region ORDER BY day, id
                                 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        FROM sales ORDER BY region, day, id""").fetchall()


def running_totals_default_frame(conn: sqlite3.Connection) -> list[tuple]:
    """Wrong-but-tempting: default RANGE frame; same-day sales are peers."""
    return conn.execute("""
        SELECT region, id, day, amount,
               SUM(amount) OVER (PARTITION BY region ORDER BY day)
        FROM sales ORDER BY region, day, id""").fetchall()


def daily_change(conn: sqlite3.Connection) -> list[tuple]:
    return conn.execute("""
        WITH daily AS (
            SELECT region, day, SUM(amount) AS total FROM sales GROUP BY region, day
        )
        SELECT region, day, total,
               total - LAG(total) OVER (PARTITION BY region ORDER BY day)
        FROM daily ORDER BY region, day""").fetchall()


def main() -> None:
    conn = make_db()
    top2 = top_n_per_region(conn, 2)
    print("top 2 per region:", top2)
    print("== correlated:", top2 == top_n_correlated(conn, 2),
          "| == python:", top2 == top_n_python(SALES, 2))
    print("east ranks (amount, row_number, rank, dense_rank):", rank_styles(conn, "east"))
    good = [r[-1] for r in running_totals(conn) if r[0] == "east"]
    bad = [r[-1] for r in running_totals_default_frame(conn) if r[0] == "east"]
    print("east running, ROWS frame:   ", good)
    print("east running, default RANGE:", bad)
    print("east daily change:", [r[2:] for r in daily_change(conn) if r[0] == "east"])
    try:
        conn.execute("SELECT id FROM sales WHERE ROW_NUMBER() OVER (ORDER BY id) <= 2")
    except sqlite3.OperationalError as e:
        print("window in WHERE:", e)
    print("n = 0:", top_n_per_region(conn, 0), "| n = 9 rows:", len(top_n_per_region(conn, 9)))
    conn.close()


if __name__ == "__main__":
    main()
