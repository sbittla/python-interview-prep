"""
Exercise 08 — Joins: Inner, Left, Anti and Self   [Tier: ★ Core]
Chapter 30 · Pattern: JOIN ... ON, LEFT JOIN + IS NULL, self-join, hash join · Target time: 25 min

Problem
-------
Tables: departments(id, name) and employees(id, name, dept_id, manager_id, salary).
`dept_id` and `manager_id` may be NULL. Write one query per function:

1. `staff_with_dept(conn)` -> (employee, department) for employees that have a
   department, ordered by employee name (INNER JOIN);
2. `headcount(conn)` -> (department, n) for EVERY department, including empty ones with
   n = 0, ordered by name (LEFT JOIN);
3. `empty_departments(conn)` -> [name] of departments with no employees (anti-join);
4. `out_earn_manager(conn)` -> (employee, salary, manager, manager_salary) where the
   employee earns more than their manager (self-join), ordered by employee;
5. `hash_join(left, right, lkey, rkey)` in plain Python: inner-join two lists of dicts in
   O(n + m + output), the way you would explain a database hash join.

Examples
--------
See main(): Legal has no staff, Flo has no department, Cy and Ed out-earn their managers.

Constraints
-----------
- Standard library sqlite3; one statement per query.

Hints
-----
- `COUNT(e.id)` counts only matched rows; `COUNT(*)` counts the NULL-padded row as 1.
- A condition on the right table belongs in ON, not WHERE: `WHERE e.salary > 100` throws
  away the NULL-padded rows and silently turns the LEFT JOIN into an INNER JOIN.
- Self-join: alias the same table twice: `employees e JOIN employees m ON e.manager_id = m.id`.

Edge cases
----------
- Department with no staff, employee with no department, the top manager (NULL
  manager_id) — never in the self-join result, duplicate keys in hash_join (every match
  pairs), NULL keys (never equal, also in Python).

Follow-ups
----------
- FULL OUTER JOIN: supported by SQLite from 3.39.0; otherwise LEFT JOIN UNION the
  anti-join of the other side.
- Anti-join three ways: LEFT JOIN ... IS NULL, NOT EXISTS, NOT IN (NOT IN breaks on NULL;
  → ex09).
"""
from __future__ import annotations

import sqlite3
from collections import defaultdict
from typing import Any

DEPARTMENTS = [(1, "Eng"), (2, "Sales"), (3, "Legal")]
EMPLOYEES = [  # id, name, dept_id, manager_id, salary
    (1, "Ada", 1, None, 200), (2, "Ben", 1, 1, 150), (3, "Cy", 1, 1, 210),
    (4, "Di", 2, 1, 120), (5, "Ed", 2, 4, 130), (6, "Flo", None, 1, 90),
]


def make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT NOT NULL,
            dept_id INTEGER REFERENCES departments(id),
            manager_id INTEGER REFERENCES employees(id), salary INTEGER NOT NULL);
    """)
    conn.executemany("INSERT INTO departments VALUES (?, ?)", DEPARTMENTS)
    conn.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?)", EMPLOYEES)
    conn.commit()
    return conn


def staff_with_dept(conn: sqlite3.Connection) -> list[tuple]:
    raise NotImplementedError("TODO")


def headcount(conn: sqlite3.Connection) -> list[tuple]:
    raise NotImplementedError("TODO")


def empty_departments(conn: sqlite3.Connection) -> list[str]:
    raise NotImplementedError("TODO")


def out_earn_manager(conn: sqlite3.Connection) -> list[tuple]:
    raise NotImplementedError("TODO")


def nested_loop_join(left: list[dict], right: list[dict], lkey: str, rkey: str) -> list[tuple]:
    raise NotImplementedError("TODO")


def hash_join(left: list[dict], right: list[dict], lkey: str, rkey: str) -> list[tuple]:
    raise NotImplementedError("TODO")


def main() -> None:
    conn = make_db()
    print("inner:", staff_with_dept(conn))
    print("headcount (LEFT, COUNT(e.id)):", headcount(conn))
    print("headcount with COUNT(*):", conn.execute("""
        SELECT d.name, COUNT(*) FROM departments d
        LEFT JOIN employees e ON e.dept_id = d.id
        GROUP BY d.id ORDER BY d.name""").fetchall())
    print("empty departments:", empty_departments(conn))
    print("filter in WHERE:", conn.execute("""
        SELECT d.name, COUNT(e.id) FROM departments d
        LEFT JOIN employees e ON e.dept_id = d.id
        WHERE e.salary > 125 GROUP BY d.id ORDER BY d.name""").fetchall())
    print("filter in ON:   ", conn.execute("""
        SELECT d.name, COUNT(e.id) FROM departments d
        LEFT JOIN employees e ON e.dept_id = d.id AND e.salary > 125
        GROUP BY d.id ORDER BY d.name""").fetchall())
    print("out-earn manager:", out_earn_manager(conn))
    emps = [dict(zip(("id", "name", "dept_id"), e[:3])) for e in EMPLOYEES]
    depts = [dict(zip(("id", "name"), d)) for d in DEPARTMENTS]
    pairs = hash_join(emps, depts, "dept_id", "id")
    print("hash join:", sorted((e["name"], d["name"]) for e, d in pairs))
    print("same as nested loop:", pairs == nested_loop_join(emps, depts, "dept_id", "id"))
    conn.close()


if __name__ == "__main__":
    main()
