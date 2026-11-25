"""
Exercise 07 — Time Series: Gaps, Resampling, Calendar Features       [Tier: ★ Core]
Chapter 34 · Pattern: DatetimeIndex, reindex/asfreq, resample · Target time: 20 min

Problem
-------
`data/daily_sales.csv` has (date, store, revenue) for March 2026, but some
store-days are missing (no row at all).
1. `missing_days(sales)` — {store: [ISO dates with no row]} for every day
   between that store's first and last date.
2. `complete_daily(sales)` — one row per store per day of that store's range,
   revenue 0.0 on missing days, plus bool column `filled`. Columns date,
   store, revenue, filled; sorted by store, date; fresh index.
3. `weekly_totals(sales)` — revenue per store per calendar week that ENDS on
   Sunday (pandas freq "W" = "W-SUN"); columns store, week_end (ISO),
   revenue (2 dp); sorted by store, week_end.
4. `weekday_vs_weekend(sales)` — mean revenue per store for weekdays vs
   weekends: dict {store: (weekday_mean, weekend_mean)} rounded to 2 dp,
   using only rows that exist.
5. `sql_weekly_totals(conn)` — (3) in SQLite.

Examples
--------
>>> missing_days(sales)["south"]
['2026-03-21']

Constraints
-----------
- One row per (store, date) at most; dates are ISO strings in the file.

Hints
-----
- pd.date_range(start, end, freq="D") is inclusive of both ends.
- groupby("store")[...].resample("W") or pd.Grouper(key="date", freq="W").
- "W" bins are labelled by their RIGHT edge (the Sunday) and closed on the
  right; a Sunday belongs to the week that ends that day.
- dt.day_of_week: Monday = 0 ... Sunday = 6 (the old spelling dt.dayofweek
  warns as deprecated in the pandas 3.1 used here). SQLite strftime('%w'): Sunday = 0.
- Month-end alias is "ME" in pandas >= 2.2; plain "M" raises in pandas 3.

Follow-ups
----------
- Missing day: fill 0 (no sales) or NaN (no data)? It changes every mean.
- Time zones: tz_localize then tz_convert; never compare naive with aware.
- Business days only: freq="B" or a custom holiday calendar.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)


def load_sales() -> pd.DataFrame:
    return pd.read_csv(DATA / "daily_sales.csv", parse_dates=["date"])


def brute_force_missing(sales: pd.DataFrame) -> dict[str, list[str]]:
    raise NotImplementedError("TODO")


def complete_daily(sales: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError("TODO")


def missing_days(sales: pd.DataFrame) -> dict[str, list[str]]:
    raise NotImplementedError("TODO")


def weekly_totals(sales: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError("TODO")


def weekday_vs_weekend(sales: pd.DataFrame) -> dict[str, tuple[float, float]]:
    raise NotImplementedError("TODO")


# Week ending Sunday: add (7 - %w) % 7 days, where %w is 0 on Sunday.
SQL_WEEKLY = """
-- TODO: write the query
"""


def sql_weekly_totals(conn: sqlite3.Connection) -> pd.DataFrame:
    raise NotImplementedError("TODO")


def main() -> None:
    sales = load_sales()
    gaps = missing_days(sales)
    print("missing days:", gaps, "| brute force agrees:", gaps == brute_force_missing(sales))
    full = complete_daily(sales)
    print("rows:", len(sales), "->", len(full), "after filling gaps")
    print(full[full["filled"]].assign(date=lambda d: d["date"].dt.strftime("%Y-%m-%d")).to_string(index=False))
    weekly = weekly_totals(sales)
    print("weekly totals (weeks end Sunday):")
    print(weekly[weekly["store"] == "north"].to_string(index=False))
    with closing(sqlite3.connect(":memory:")) as conn:
        sales.assign(date=sales["date"].dt.strftime("%Y-%m-%d")).to_sql("sales", conn, index=False)
        print("SQL weekly matches:", sql_weekly_totals(conn).equals(weekly))
    print("weekday vs weekend mean:", weekday_vs_weekend(sales))
    print("2026-03-01 is a", date(2026, 3, 1).strftime("%A"), "-> its week ends the same day")
    print("month ends ('ME'):", list(pd.date_range("2026-01-01", periods=3, freq="ME").strftime("%Y-%m-%d")))


if __name__ == "__main__":
    main()
