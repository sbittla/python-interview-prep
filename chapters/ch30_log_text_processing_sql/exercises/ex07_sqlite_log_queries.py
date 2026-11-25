"""
Exercise 07 — Load a Log into SQLite and Query It   [Tier: ★ Core]
Chapter 30 · Pattern: sqlite3 + SELECT/WHERE/GROUP BY/HAVING/ORDER BY · Target time: 25 min

Problem
-------
1. `make_db(hits)` -> an in-memory `sqlite3.Connection` with table
   hits(ip TEXT, ts INTEGER, method TEXT, path TEXT, status INTEGER CHECK (status BETWEEN
   100 AND 599), latency_ms INTEGER), filled with `executemany` and `?` placeholders.
2. `path_report(conn, min_hits)` -> rows (path, hits, avg_latency_ms rounded to an int,
   errors = count of status >= 500) for paths with at least `min_hits` hits, ordered by
   hits descending, then path.
3. `client_errors(conn)` -> rows (ip, n) counting 4xx responses per ip, n descending, ip.
4. `find_by_path(conn, path)` -> the matching rows, parameterised (safe), and
   `find_by_path_unsafe` built with an f-string, to show injection.
5. `insert_atomic(conn, rows)` -> insert all rows or none (use `with conn:`).

Examples
--------
>>> conn = make_db([("a", 0, "GET", "/x", 200, 10), ("b", 1, "GET", "/x", 503, 30)])
>>> path_report(conn, 1)
[('/x', 2, 20, 1)]

Constraints
-----------
- Standard library `sqlite3` only; the SQL must do the aggregation, not Python.

Hints
-----
- Logical order: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT.
  WHERE filters rows before grouping; HAVING filters groups after it.
- `SUM(status >= 500)` counts matches: comparisons are 0/1 in SQLite. Portable SQL
  writes `SUM(CASE WHEN status >= 500 THEN 1 ELSE 0 END)`.
- `CAST(ROUND(AVG(x)) AS INTEGER)` gives an int. Note `7 / 2` is integer division (3).
- SQLite's ROUND() rounds halves away from zero (154.5 -> 155.0); Python's round()
  rounds halves to even (154.5 -> 154). A Python cross-check must use the same rule.

Edge cases
----------
- min_hits above every count (empty list), NULL latency (AVG ignores NULLs; COUNT(col)
  skips them, COUNT(*) does not), `x = NULL` is never true (use IS NULL), a CHECK
  violation mid-batch (the whole batch must roll back).

Follow-ups
----------
- Speed up `find_by_path`: `CREATE INDEX idx_hits_path ON hits(path)`; check with
  `EXPLAIN QUERY PLAN`.
- `with conn:` commits or rolls back but does NOT close the connection; use
  `contextlib.closing(conn)` or call `conn.close()`.
"""
from __future__ import annotations

import re
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

DATA = Path(__file__).resolve().parent.parent / "data"
HIT_RE = re.compile(r'(\S+) \S+ \S+ \[([^\]]+)\] "([A-Z]+) (\S+) [^"]*" (\d{3}) (?:\d+|-) (\d+\.\d+)')
Row = tuple[str, int, str, str, int, int]

SCHEMA = """
CREATE TABLE hits (
    ip TEXT NOT NULL, ts INTEGER NOT NULL, method TEXT NOT NULL, path TEXT NOT NULL,
    status INTEGER NOT NULL CHECK (status BETWEEN 100 AND 599), latency_ms INTEGER
)"""


def load_rows(path: Path = DATA / "access.log") -> list[Row]:
    """Condensed ex01 parser (given)."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = HIT_RE.fullmatch(line.rstrip("\r\n"))
            if not m:
                continue
            try:
                ts = datetime.strptime(m[2], "%d/%b/%Y:%H:%M:%S %z")
            except ValueError:
                continue
            rows.append((m[1], int(ts.timestamp()), m[3], m[4], int(m[5]),
                         round(float(m[6]) * 1000)))
    return rows


def make_db(rows: Iterable[Row]) -> sqlite3.Connection:
    raise NotImplementedError("TODO")


def path_report(conn: sqlite3.Connection, min_hits: int) -> list[tuple]:
    raise NotImplementedError("TODO")


def client_errors(conn: sqlite3.Connection) -> list[tuple]:
    raise NotImplementedError("TODO")


def python_path_report(rows: list[Row], min_hits: int) -> list[tuple]:
    """Rung 1, used as a cross-check."""
    raise NotImplementedError("TODO")


def find_by_path(conn: sqlite3.Connection, path: str) -> list[tuple]:
    raise NotImplementedError("TODO")


def find_by_path_unsafe(conn: sqlite3.Connection, path: str) -> list[tuple]:
    # NEVER do this: the value becomes part of the SQL text.
    return conn.execute(f"SELECT ip, status FROM hits WHERE path = '{path}' ORDER BY ts, ip"
                        ).fetchall()


def insert_atomic(conn: sqlite3.Connection, rows: list[Row]) -> None:
    raise NotImplementedError("TODO")


def main() -> None:
    rows = load_rows()
    conn = make_db(rows)
    print("rows:", conn.execute("SELECT COUNT(*) FROM hits").fetchone()[0])
    report = path_report(conn, 5)
    for r in report:
        print("  ", r)
    print("SQL == Python:", report == python_path_report(rows, 5))
    print("4xx by ip:", client_errors(conn))
    attack = "x' OR '1'='1"
    print("safe:", len(find_by_path(conn, attack)), "rows | unsafe:",
          len(find_by_path_unsafe(conn, attack)), "rows")
    try:
        insert_atomic(conn, [("1.1.1.1", 0, "GET", "/ok", 200, 1),
                             ("1.1.1.1", 1, "GET", "/bad", 999, 1)])
    except sqlite3.IntegrityError as e:
        print("rolled back:", e, "| rows:", conn.execute("SELECT COUNT(*) FROM hits").fetchone()[0])
    print("pitfalls:", conn.execute("SELECT 7 / 2, 7 / 2.0, NULL = NULL, NULL IS NULL").fetchone())
    print("ROUND(154.5) in SQLite:", conn.execute("SELECT ROUND(154.5)").fetchone()[0],
          "| Python round(154.5):", round(154.5))
    conn.execute("CREATE TABLE t (x INTEGER)")
    conn.executemany("INSERT INTO t VALUES (?)", [(1,), (None,), (3,)])
    print("COUNT(*), COUNT(x), AVG(x):",
          conn.execute("SELECT COUNT(*), COUNT(x), AVG(x) FROM t").fetchone())
    conn.row_factory = sqlite3.Row                     # rows addressable by column name
    top = conn.execute("SELECT path, COUNT(*) AS n FROM hits GROUP BY path "
                       "ORDER BY n DESC, path LIMIT 1").fetchone()
    print("sqlite3.Row:", top["path"], top["n"], "| empty HAVING:", path_report(conn, 99))
    conn.close()


if __name__ == "__main__":
    main()
