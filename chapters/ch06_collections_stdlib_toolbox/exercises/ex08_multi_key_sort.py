"""
Exercise 08 — Multi-Key Stable Sorting of Records              [Tier: ★ Core]
Chapter 06 · Pattern: sort keys, stability, namedtuple records · Target time: 15 min

Problem
-------
Employees are `Employee(name, dept, salary, age)` named tuples.

1. `payroll_order(rows)` — sort by dept ascending, then salary DESCENDING,
   then name ascending. Return a new list.
2. `multi_sort(rows, spec)` — `spec` is a list of (field_name, descending)
   pairs, most important first, e.g. [("dept", False), ("name", True)].
   Sort by all of them, where ANY field (including strings) may be descending.
   Rows equal on every field keep their input order.

Examples
--------
>>> rows = [Employee("Bo", "eng", 90, 30), Employee("Al", "eng", 90, 41),
...         Employee("Cy", "art", 70, 25)]
>>> [e.name for e in payroll_order(rows)]
['Cy', 'Al', 'Bo']
>>> [e.name for e in multi_sort(rows, [("dept", False), ("name", True)])]
['Cy', 'Bo', 'Al']

Constraints
-----------
- Up to 10**5 rows, up to 4 sort fields.

Hints
-----
- `operator.attrgetter("dept")` is a fast key for named tuples.
- `reverse=True` keeps stability (equal items stay in input order).

Follow-ups
----------
- Sorting `None` values: key `(x is None, x)` puts them last (→ §7.19).
- `sorted()` returns a new list; `list.sort()` sorts in place and returns None.
"""
from __future__ import annotations

from collections import namedtuple
from functools import cmp_to_key
from operator import attrgetter

Employee = namedtuple("Employee", "name dept salary age")


def payroll_order(rows: list[Employee]) -> list[Employee]:
    raise NotImplementedError("TODO")


def by_comparator(rows: list[Employee], spec: list[tuple[str, bool]]) -> list[Employee]:
    raise NotImplementedError("TODO")


def multi_sort(rows: list[Employee], spec: list[tuple[str, bool]]) -> list[Employee]:
    raise NotImplementedError("TODO")


def main() -> None:
    rows = [
        Employee("Bo", "eng", 90, 30), Employee("Al", "eng", 90, 41),
        Employee("Cy", "art", 70, 25), Employee("Di", "eng", 120, 35),
        Employee("Ed", "art", 70, 52), Employee("Fa", "ops", 60, 29),
    ]
    print("payroll_order:", [e.name for e in payroll_order(rows)])
    spec = [("dept", False), ("name", True)]
    print("dept asc, name desc:", [e.name for e in multi_sort(rows, spec)])
    spec2 = [("salary", True), ("age", False)]
    print("salary desc, age asc:", [(e.name, e.salary, e.age) for e in multi_sort(rows, spec2)])
    print("agrees with comparator:",
          multi_sort(rows, spec) == by_comparator(rows, spec),
          multi_sort(rows, spec2) == by_comparator(rows, spec2))
    pairs = [("b", 1), ("a", 2), ("b", 0), ("a", 1)]
    print("stable sort by letter only:", sorted(pairs, key=lambda p: p[0]))
    e = rows[0]
    print("namedtuple:", e, "| e.salary =", e.salary, "| e._replace(age=31).age =", e._replace(age=31).age)


if __name__ == "__main__":
    main()
