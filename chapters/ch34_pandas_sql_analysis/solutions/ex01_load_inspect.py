"""
Exercise 01 — Load, Type and Profile a CSV                           [Tier: ★ Core]
Chapter 34 · Pattern: read_csv with dtypes, Series alignment · Target time: 15 min

Problem
-------
`data/orders.csv` has columns order_id, user_id, order_date, amount, status.
1. `load_orders(path)` — read it so that order_date is datetime64 and amount is
   float (blank cells become NaN). Keep the file's row order.
2. `profile(df)` — return a plain dict:
   {"rows": int, "columns": [names...], "nulls": {col: count, ...} (only
   columns with at least one null), "users": distinct user_id count,
   "first": "YYYY-MM-DD", "last": "YYYY-MM-DD"}.  first/last are None for an
   empty frame.
3. `brute_force_profile(path)` — the same dict using only the csv module.
4. `add_aligned(a, b)` — two Series indexed by label; return a + b where a
   label missing on one side counts as 0 (plain `a + b` gives NaN there),
   sorted by label.

Examples
--------
>>> add_aligned(pd.Series({"x": 1, "y": 2}), pd.Series({"y": 10, "z": 5})).to_dict()
{'x': 1.0, 'y': 12.0, 'z': 5.0}

Constraints
-----------
- Up to ~10**6 rows; pandas, numpy and the standard library only.

Approach ladder
---------------
1. Brute force — csv.DictReader, count blanks and distinct users in Python
   loops: O(n) time, O(u) space for the user set, but every value is a Python
   str and every date comparison is a string comparison.
2. Optimal    — read_csv(parse_dates=..., dtype=...): one C-level pass, typed
   columns; df.isna().sum(), Series.nunique(), min()/max() are vectorised
   O(n) column scans (nunique hashes: O(n) average).
   Why move up: typed columns make every later step (filters, groupby,
   resample) correct and fast; the loop version has to re-parse strings.

Hints
-----
- read_csv(parse_dates=["order_date"]) and dtype={"order_id": "int64"}.
- An integer column with a blank cell cannot stay int64: it becomes float64.
- Series arithmetic aligns on the index; .add(other, fill_value=0) fills gaps.

Follow-ups
----------
- How do you read a 10 GB CSV? (chunksize=, usecols=, dtype=; → §30.5)
- Why is `status` read as the "str" dtype and not object in pandas 3?
- What changes if user_id has blanks? (int64 cannot hold NaN: use "Int64".)
"""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)


def load_orders(path: Path = DATA / "orders.csv") -> pd.DataFrame:
    return pd.read_csv(
        path,
        dtype={"order_id": "int64", "user_id": "int64", "amount": "float64"},
        parse_dates=["order_date"],
    )


def profile(df: pd.DataFrame) -> dict:
    nulls = df.isna().sum()
    empty = df.empty
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "nulls": {c: int(n) for c, n in nulls.items() if n > 0},
        "users": int(df["user_id"].nunique()),
        "first": None if empty else df["order_date"].min().strftime("%Y-%m-%d"),
        "last": None if empty else df["order_date"].max().strftime("%Y-%m-%d"),
    }


def brute_force_profile(path: Path = DATA / "orders.csv") -> dict:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        rows, users, dates = 0, set(), []
        nulls = dict.fromkeys(columns, 0)
        for row in reader:
            rows += 1
            for c in columns:
                nulls[c] += row[c] == ""
            users.add(int(row["user_id"]))
            dates.append(row["order_date"])          # ISO dates sort as strings
    return {
        "rows": rows,
        "columns": columns,
        "nulls": {c: n for c, n in nulls.items() if n > 0},
        "users": len(users),
        "first": min(dates) if dates else None,
        "last": max(dates) if dates else None,
    }


def add_aligned(a: pd.Series, b: pd.Series) -> pd.Series:
    return a.add(b, fill_value=0).astype("float64").sort_index()


def main() -> None:
    df = load_orders()
    print("shape:", df.shape)
    types = pd.api.types
    print("ids int64:", (df[["order_id", "user_id"]].dtypes == "int64").all(),
          "| date is datetime:", types.is_datetime64_any_dtype(df["order_date"]),
          "| amount float:", types.is_float_dtype(df["amount"]),
          "| status string:", types.is_string_dtype(df["status"]))
    print("profile == brute force:", profile(df) == brute_force_profile())
    for k, v in profile(df).items():
        print(f"  {k}: {v}")
    print("first rows:")
    print(df.head(3).to_string(index=False))
    print("type(df['amount']):", type(df["amount"]).__name__,
          "| type(df[['amount']]):", type(df[["amount"]]).__name__)
    a = pd.Series({"x": 1, "y": 2})
    b = pd.Series({"y": 10, "z": 5})
    print("a + b          :", (a + b).to_dict())
    print("add_aligned    :", add_aligned(a, b).to_dict())
    print("empty profile  :", profile(df.iloc[0:0]))


if __name__ == "__main__":
    main()
