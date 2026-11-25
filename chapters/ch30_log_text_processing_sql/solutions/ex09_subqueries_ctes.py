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

Examples
--------
>>> nth_highest_salary(make_db(), 2)
200
>>> nth_highest_salary(make_db(), 99) is None
True

Constraints
-----------
- SQLite supports WITH and WITH RECURSIVE (since 3.8.3); the venv runs 3.50.

Approach ladder (above_dept_avg)
--------------------------------
1. Correlated subquery — logically re-runs AVG for every employee: O(n^2) without an
   index on dept_id (each of n rows scans the table).
2. CTE that groups once (dept_id -> avg), joined back: one grouping pass (a sort or a
   temporary B-tree, O(n log n)) plus n lookups into d groups. Why move up: one
   aggregation pass, and the CTE has a name you can run and test on its own.
3. Window function `AVG(salary) OVER (PARTITION BY dept_id)` in a CTE, then filter:
   one pass, no join (→ ex10).

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
  one (never above its own average), cycles in manager_id (UNION instead of UNION ALL,
  or a depth limit, stops infinite recursion).

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
    return conn.execute("""
        SELECT e.name, e.salary FROM employees e
        WHERE e.salary > (SELECT AVG(x.salary) FROM employees x WHERE x.dept_id = e.dept_id)
        ORDER BY e.name""").fetchall()


def above_dept_avg_cte(conn: sqlite3.Connection) -> list[tuple]:
    return conn.execute("""
        WITH dept_avg AS (
            SELECT dept_id, AVG(salary) AS avg_salary FROM employees GROUP BY dept_id
        )
        SELECT e.name, e.salary
        FROM employees e JOIN dept_avg a ON a.dept_id = e.dept_id
        WHERE e.salary > a.avg_salary
        ORDER BY e.name""").fetchall()


def nth_highest_salary(conn: sqlite3.Connection, n: int) -> int | None:
    return conn.execute("""
        SELECT (SELECT DISTINCT salary FROM employees
                ORDER BY salary DESC LIMIT 1 OFFSET ?)""", (n - 1,)).fetchone()[0]


def non_managers(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("""
        SELECT e.name FROM employees e
        WHERE NOT EXISTS (SELECT 1 FROM employees r WHERE r.manager_id = e.id)
        ORDER BY e.name""").fetchall()
    return [name for (name,) in rows]


def non_managers_not_in(conn: sqlite3.Connection) -> list[str]:
    """Wrong-but-tempting: manager_id contains NULL, so NOT IN is never TRUE."""
    rows = conn.execute("""
        SELECT name FROM employees
        WHERE id NOT IN (SELECT manager_id FROM employees)
        ORDER BY name""").fetchall()
    return [name for (name,) in rows]


def org_chart(conn: sqlite3.Connection) -> list[tuple]:
    return conn.execute("""
        WITH RECURSIVE chart(id, name, depth, path) AS (
            SELECT id, name, 0, name FROM employees WHERE manager_id IS NULL
            UNION ALL
            SELECT e.id, e.name, c.depth + 1, c.path || '/' || e.name
            FROM employees e JOIN chart c ON e.manager_id = c.id
        )
        SELECT depth, name, path FROM chart ORDER BY path""").fetchall()


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
    conn.close()


if __name__ == "__main__":
    main()
