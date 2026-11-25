# Chapter 34 — Pandas and SQL for Analysis

Manuscript: `manuscript/ch34_pandas_sql_analysis.md`. Packages: pandas, numpy, stdlib `sqlite3`.
Verified with pandas 3.1.1, NumPy 2.5.5, SQLite 3.50.4 (window functions need SQLite ≥ 3.25,
`RANGE ... PRECEDING` offsets ≥ 3.28), CPython 3.13; code is written for Python 3.10+.
Every solution pairs pandas with an equivalent SQL query on an in-memory SQLite database, and the
tests cross-check the two.

| ID | Title | Tier | Pattern | Sections |
|---|---|---|---|---|
| ex01 | Load, type and profile a CSV | ★ Core | `read_csv` dtypes, `isna().sum()`, index alignment | 34.1 |
| ex02 | Selection with loc, iloc and masks | ★ Core | boolean mask = `WHERE`, `.loc` assignment, copy-on-write | 34.2 |
| ex03 | Missing data: impute, count, NaN vs NULL | ★ Core | `transform("median")`, `groupby(dropna=False)` | 34.3 |
| ex04 | Country scorecard | ★ Core | named aggregation, `transform` = `SUM() OVER` | 34.4 |
| ex05 | Joins: inner, left, anti, duplicate keys | ★ Core | `merge(indicator=, validate=)`, hash join | 34.5 |
| ex06 | Pivot tables and melt | ◆ Extended | `pivot_table` = `SUM(CASE WHEN ...)`, `melt` | 34.6 |
| ex07 | Time series: gaps, weeks, weekdays | ★ Core | `reindex(date_range)`, `Grouper(freq="W")` | 34.7 |
| ex08 | Rolling, running and lag features | ★ Core | `cumsum`/`shift`/`rolling(7)` vs `rolling("7D")` | 34.8 |
| ex09 | Monthly cohort retention matrix | ★ Core | cohort key + month offset + `unstack` | 34.9 |
| ex10 | Ordered conversion funnel | ◆ Extended | per-step merge + `ts >= t_prev` + `min` | 34.9 |
| ex11 | Nth highest, latest row, streaks | ◆ Extended | `DENSE_RANK`, `ROW_NUMBER`, gaps-and-islands | 34.9, 34.10 |

Data (in `data/`, read via `Path(__file__).resolve().parent.parent / "data"`):
`users.csv` (40 users, 2 with blank country), `orders.csv` (87 rows: 3 blank amounts, one exact
duplicate row, one order from unknown user 99), `events.csv` (funnel events, two users purchase
before viewing), `daily_sales.csv` (two stores, March 2026, three missing store-days).

## How to run

```bash
OPENBLAS_NUM_THREADS=4 .venv/Scripts/python chapters/ch34_pandas_sql_analysis/solutions/ex09_cohort_retention.py
.venv/Scripts/python -m pytest chapters/ch34_pandas_sql_analysis                       # reference solutions
TARGET=exercises .venv/Scripts/python -m pytest chapters/ch34_pandas_sql_analysis      # your stubs
.venv/Scripts/python tools/run_all.py --chapter 34                                     # regenerate outputs/
```

Each solution docstring holds the full statement, approach ladder (with complexity), hints and
follow-ups; `exercises/` holds the same file with the ladder removed, function bodies replaced by
`raise NotImplementedError("TODO")` and SQL strings blanked. Outputs avoid dtype reprs and are
sorted. They were generated (and only verified) on pandas 3.1.1; on pandas 2.x without copy-on-write,
ex02's chained-assignment line behaves differently, and ex07 needs `"ME"`-era aliases (pandas ≥ 2.2).
