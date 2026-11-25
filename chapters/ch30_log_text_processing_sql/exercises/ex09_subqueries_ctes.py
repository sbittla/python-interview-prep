"""
Exercise 09 — Subqueries, CTEs and a Recursive Org Chart   [Tier: ◆ Extended]
Chapter 30 · Pattern: scalar / correlated subquery, WITH, WITH RECURSIVE · Target time: 30 min

Problem
-------
Same HR tables as ex08: departments(id, name), employees(id, name, dept_id, manager_id,
salary). Write

1. `above_dept_avg(conn)` and `above_dept_avg_cte(conn)` -> (name, salary) of employees
   paid more than their own department's average, ordered by name: once with a
   correlated subquery, once with a CTE + join. Both must agree.
2. `nth_highest_salary(conn, n)` -> the n-th highest DISTINCT salary, or None if there
   are fewer than n distinct salaries (one row, never zero rows).
3. `non_managers(conn)` -> names of employees who manage nobody, ordered by name. Use
   NOT EXISTS; also show why `NOT IN (SELECT manager_id ...)` returns nothing here.
4. `org_chart(conn)` -> (depth, name, path) for every employee via WITH RECURSIVE,
   starting at the employee whose manager_id IS NULL (depth 0), ordered by path.
5. `manager_chain(conn, name)` -> [name, manager, manager's manager, ...], walking up
   manager_id; must terminate even if the data contains a cycle.

Examples
--------
>>> nth_highest_salary(make_db(), 2)
200
>>> nth_highest_salary(make_db(), 99) is None
True

Constraints
-----------
- SQLite supports WITH and WITH RECURSIVE (since 3.8.3); the venv runs 3.50.

Hints
-----
- `SELECT (SELECT ... LIMIT 1 OFFSET ?)` wraps a query that may return no row into a
  scalar subquery that returns NULL instead.
- `x NOT IN (1, NULL)` is never TRUE: `x <> NULL` is NULL, and NOT IN needs every
  comparison to be TRUE.
- The recursive CTE = anchor SELECT UNION ALL step SELECT that joins the CTE itself.

Edge cases
----------
- n larger than the number of distinct salaries, duplicate salaries (DISTINCT), employee
  with NULL dept_id (excluded by both versions: `NULL = NULL` is not TRUE), a department of
  one (never above its own average), cycles in manager_id: UNION stops a cycle only if the
  CTE has no counter or path column; with depth/path every row is new, so add
  `WHERE depth < N` or a path check (`manager_chain` below).

Follow-ups
----------
- Total salary under each manager (the whole subtree): recursive CTE carrying the root id.
- Department with the highest payroll: CTE + ORDER BY ... LIMIT 1, or RANK() for ties.
"""
from __future__ import annotations

import sqlite3

DEPARTMENTS = [(1, "Eng"), (2, "Sales"), (3, "Legal")]
EMPLOYEES = [  # id, name, dept_id, manager_id, salary
    (1, "Ada", 1, None, 200), (2, "Ben", 1, 1, 150), (3, "Cy", 1, 1, 210),
    (4, "Di", 2, 1, 120), (5, "Ed", 2, 4, 130), (6, "Flo", None, 1, 90),
    (7, "Gil", 2, 4, 130),
]


def make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT NOT NULL,
            dept_id INTEGER, manager_id INTEGER, salary INTEGER NOT NULL);
    """)
    conn.executemany("INSERT INTO departments VALUES (?, ?)", DEPARTMENTS)
    conn.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?)", EMPLOYEES)
    conn.commit()
    return conn


def above_dept_avg(conn: sqlite3.Connection) -> list[tuple]:
    raise NotImplementedError("TODO")


def above_dept_avg_cte(conn: sqlite3.Connection) -> list[tuple]:
    raise NotImplementedError("TODO")


def nth_highest_salary(conn: sqlite3.Connection, n: int) -> int | None:
    raise NotImplementedError("TODO")


def non_managers(conn: sqlite3.Connection) -> list[str]:
    raise NotImplementedError("TODO")


def non_managers_not_in(conn: sqlite3.Connection) -> list[str]:
    """Wrong-but-tempting: manager_id contains NULL, so NOT IN is never TRUE."""
    rows = conn.execute("""
        SELECT name FROM employees
        WHERE id NOT IN (SELECT manager_id FROM employees)
        ORDER BY name""").fetchall()
    return [name for (name,) in rows]


def org_chart(conn: sqlite3.Connection) -> list[tuple]:
    raise NotImplementedError("TODO")


def manager_chain(conn: sqlite3.Connection, name: str) -> list[str]:
    raise NotImplementedError("TODO")


def cycle_demo() -> tuple[int, int]:
    """Rows produced on a 2-node cycle by UNION with a depth column (bounded at 10 so it
    cannot hang) vs plain UNION without one."""
    raise NotImplementedError("TODO")


def main() -> None:
    conn = make_db()
    print("above dept avg (correlated):", above_dept_avg(conn))
    print("above dept avg (CTE):       ", above_dept_avg_cte(conn))
    print("2nd/3rd/99th highest:", [nth_highest_salary(conn, n) for n in (2, 3, 99)])
    print("non-managers NOT EXISTS:", non_managers(conn))
    print("non-managers NOT IN:    ", non_managers_not_in(conn))
    print("NOT IN with a NULL:", conn.execute("SELECT 3 NOT IN (1, NULL), 3 NOT IN (1, 2)").fetchone())
    for depth, name, path in org_chart(conn):
        print("  " * depth + f"{name:<4} {path}")
    print("chain from Ed:", manager_chain(conn, "Ed"))
    conn.execute("UPDATE employees SET manager_id = 5 WHERE id = 1")     # Ada <- Ed: a cycle
    print("chain with a cycle:", manager_chain(conn, "Ed"))
    print("2-node cycle rows: UNION + depth (capped at 10) =", cycle_demo()[0],
          "| UNION, no depth =", cycle_demo()[1])
    conn.close()


if __name__ == "__main__":
    main()
