"""
Exercise 08 — Rolling, Running and Lag Features (= SQL Window Functions)  [Tier: ★ Core]
Chapter 34 · Pattern: groupby + cumsum / shift / rolling · Target time: 25 min

Problem
-------
`data/daily_sales.csv` (date, store, revenue) has missing days. Per store,
ordered by date, build `window_features(sales)` with columns:
  date, store, revenue,
  run_total — cumulative revenue so far,
  prev      — revenue of the previous ROW (NaN for the first row),
  dod_pct   — 100 * (revenue - prev) / prev, 1 dp,
  rows_7    — mean of the last 7 ROWS including this one; NaN until 7 exist,
  days_7    — mean of rows whose date is within the last 7 CALENDAR days
              (date - 6 days .. date), using whatever rows exist.
All floats rounded to 2 dp (dod_pct to 1). Sorted by store, date; fresh index.
`sql_window_features(conn)` builds the same table with SQLite window
functions; `brute_force_rows_7(values)` recomputes rows_7 with slices.
`prior_week_mean(sales)` / `sql_prior_week_mean(conn)` — per row, the mean
revenue of the 7 calendar days BEFORE the row's date (date - 7 .. date - 1,
today excluded; NaN when none exist), as a list in (store, date) order.

Examples
--------
>>> wf = window_features(sales); wf.loc[wf["store"] == "north", "rows_7"].isna().sum()
6

Constraints
-----------
- n rows, window w = 7.

Hints
-----
- Sort by (store, date) first; every window feature assumes order.
- g = df.groupby("store")["revenue"]; g.cumsum(), g.shift(1) keep row order.
- Row windows and calendar windows differ only where days are missing.
- SQL: SUM(x) OVER (PARTITION BY s ORDER BY d ROWS UNBOUNDED PRECEDING),
  LAG(x), AVG(x) OVER (... ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),
  and RANGE BETWEEN 6 PRECEDING over julianday(date) (SQLite >= 3.28).
- A time window "7D" is (d - 7 days, d]; closed="left" gives [d - 7, d), i.e.
  RANGE BETWEEN 7 PRECEDING AND 1 PRECEDING.

Follow-ups
----------
- prev on a missing day is NOT yesterday: reindex to full days first (→ ex07).
- Exponentially weighted mean: ewm(alpha=...).mean().
- Centered window: rolling(7, center=True); in SQL, ROWS BETWEEN 3 PRECEDING
  AND 3 FOLLOWING.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)
W = 7


def load_sales() -> pd.DataFrame:
    return pd.read_csv(DATA / "daily_sales.csv", parse_dates=["date"])


def brute_force_rows_7(values: list[float]) -> list[float]:
    raise NotImplementedError("TODO")


def window_features(sales: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError("TODO")


SQL_WINDOWS = """
-- TODO: write the query
"""


def sql_window_features(conn: sqlite3.Connection) -> pd.DataFrame:
    raise NotImplementedError("TODO")


def prior_week_mean(sales: pd.DataFrame) -> list[float]:
    raise NotImplementedError("TODO")


SQL_PRIOR_WEEK = """
-- TODO: write the query
"""


def sql_prior_week_mean(conn: sqlite3.Connection) -> list[float]:
    raise NotImplementedError("TODO")


def main() -> None:
    sales = load_sales()
    wf = window_features(sales)
    show = wf.assign(date=wf["date"].dt.strftime("%m-%d"))
    print("north around the 2-day gap (Mar 10-11 missing):")
    print(show[(show["store"] == "north") & show["date"].between("03-06", "03-14")].to_string(index=False))
    north = wf[wf["store"] == "north"]
    brute = brute_force_rows_7(north["revenue"].tolist())
    print("rows_7 matches brute force:",
          np.allclose(north["rows_7"], np.round(brute, 2), equal_nan=True))
    print("leading NaNs in rows_7 per store:", wf.groupby("store")["rows_7"].apply(lambda s: int(s.isna().sum())).to_dict())
    print("rows where rows_7 != days_7 (after the first 7):",
          int(((wf["rows_7"] - wf["days_7"]).abs() > 0.005).sum()))
    with closing(sqlite3.connect(":memory:")) as conn:
        sales.assign(date=sales["date"].dt.strftime("%Y-%m-%d")).to_sql("sales", conn, index=False)
        sql = sql_window_features(conn)
    num = ["revenue", "run_total", "prev", "dod_pct", "rows_7", "days_7"]
    print("SQL window functions match:",
          sql["store"].equals(wf["store"]) and sql["date"].equals(wf["date"])
          and np.allclose(sql[num].to_numpy(float), wf[num].to_numpy(float), equal_nan=True, atol=0.011))
    print("final running totals:", wf.groupby("store")["run_total"].last().to_dict())
    prior = prior_week_mean(sales)
    with closing(sqlite3.connect(":memory:")) as conn:
        sales.assign(date=sales["date"].dt.strftime("%Y-%m-%d")).to_sql("sales", conn, index=False)
        sql_prior = sql_prior_week_mean(conn)
    print("prior-7-day mean (closed='left') first 3 north:", prior[:3],
          "| matches RANGE 7..1 PRECEDING:", np.allclose(prior, sql_prior, equal_nan=True, atol=0.011))


if __name__ == "__main__":
    main()
