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

Approach ladder
---------------
1. Brute force — for each row, slice the previous w values and average:
   O(n * w). For calendar windows, scan back while date >= d - 6: O(n * w).
2. Optimal    — rolling(w) keeps a running sum: add the new value, drop the
   one leaving, O(n) total; rolling("7D", on="date") does the same with a
   two-pointer over sorted timestamps, O(n). cumsum and shift are O(n).
   Why move up: for w = 365 the slice version does 365x the work.

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
    return [float(np.mean(values[i - W + 1:i + 1])) if i >= W - 1 else float("nan")
            for i in range(len(values))]


def window_features(sales: pd.DataFrame) -> pd.DataFrame:
    df = sales.sort_values(["store", "date"]).reset_index(drop=True)
    g = df.groupby("store")["revenue"]
    df["run_total"] = g.cumsum()
    df["prev"] = g.shift(1)
    df["dod_pct"] = (100 * (df["revenue"] - df["prev"]) / df["prev"]).round(1)
    df["rows_7"] = g.transform(lambda s: s.rolling(W, min_periods=W).mean())
    days = (df.set_index("date").groupby("store")["revenue"]
            .rolling(f"{W}D").mean())               # index: (store, date), same order as df
    df["days_7"] = days.to_numpy()
    cols = ["run_total", "prev", "rows_7", "days_7"]
    df[cols] = df[cols].round(2)
    return df


SQL_WINDOWS = """
SELECT date, store, revenue,
       ROUND(SUM(revenue) OVER w_all, 2) AS run_total,
       LAG(revenue) OVER w_ord AS prev,
       ROUND(100.0 * (revenue - LAG(revenue) OVER w_ord) / LAG(revenue) OVER w_ord, 1) AS dod_pct,
       CASE WHEN COUNT(*) OVER w_rows = 7 THEN ROUND(AVG(revenue) OVER w_rows, 2) END AS rows_7,
       ROUND(AVG(revenue) OVER w_days, 2) AS days_7
FROM sales
WINDOW w_ord  AS (PARTITION BY store ORDER BY date),
       w_all  AS (PARTITION BY store ORDER BY date ROWS UNBOUNDED PRECEDING),
       w_rows AS (PARTITION BY store ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),
       w_days AS (PARTITION BY store ORDER BY julianday(date) RANGE BETWEEN 6 PRECEDING AND CURRENT ROW)
ORDER BY store, date
"""


def sql_window_features(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(SQL_WINDOWS, conn, parse_dates=["date"])


def prior_week_mean(sales: pd.DataFrame) -> list[float]:
    df = sales.sort_values(["store", "date"])
    means = (df.set_index("date").groupby("store")["revenue"]
             .rolling(f"{W}D", closed="left").mean())
    return [round(v, 2) if v == v else float("nan") for v in means.tolist()]


SQL_PRIOR_WEEK = """
SELECT AVG(revenue) OVER (PARTITION BY store ORDER BY julianday(date)
                          RANGE BETWEEN 7 PRECEDING AND 1 PRECEDING)
FROM sales ORDER BY store, date
"""


def sql_prior_week_mean(conn: sqlite3.Connection) -> list[float]:
    return [float("nan") if v is None else round(v, 2) for (v,) in conn.execute(SQL_PRIOR_WEEK)]


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
