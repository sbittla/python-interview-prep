# Chapter 34. Pandas and SQL for Analysis

★ Core · Tracks M L · Study time ≈ 6 h · Prerequisites: §30.6–§30.10 (SQL, `sqlite3`), §33.4–§33.5 (vectorising, axis aggregations)

**Learning objectives**

- Load, filter, aggregate and reshape tables in pandas without loops.
- Translate each pandas step to SQL and back.
- Handle NaN/NULL, duplicate join keys, missing days and ties deliberately.
- Solve cohort retention, funnels, N-th highest and streaks.

> **Recognise it.** "Per-X metrics from this table"; "monthly", "share of total", "rolling 7-day",
> "retention", "conversion", "second highest", "consecutive days". Frame in memory → pandas;
> "write the query" → SQL. State the grain (one row per what?) and the NULL and tie rules first.

**Version baseline.** Everything here ran on **pandas 3.1.1**, NumPy 2.5.5, SQLite 3.50.4,
CPython 3.13, no pyarrow. pandas 3 changes you will be asked about:

| pandas 3 behaviour | pandas 2.x default | Consequence |
|---|---|---|
| Copy-on-write always on | opt-in | chained assignment never writes (warns) |
| Text columns get dtype `str` (pyarrow-backed if installed, else Python) | `object` | test `is_string_dtype`, not `== object` |
| Parsed datetimes default to `datetime64[us]` (`[ns]` if the strings carry nanoseconds) | `[ns]` | don't hard-code the unit |

Use `"ME"`/`"YE"`/`"QE"` (`"M"`/`"Y"`/`"Q"` raise since 3.0); 3.1 deprecates `.dt.dayofweek`,
`.dt.weekday` and `.dt.dayofyear` for `.dt.day_of_week`/`.dt.day_of_year`.

## 34.1 Series and DataFrames; reading data

A **Series** is a 1-D array plus a label index; a **DataFrame** is a dict of Series sharing one
index. Arithmetic **aligns on labels**, not positions. Pass dtypes and `parse_dates` when reading.

```python
import io

import pandas as pd

csv = io.StringIO("order_id,user_id,order_date,amount,status\n"
                  "1001,1,2026-01-23,67.50,paid\n"
                  "1002,2,2026-01-25,,paid\n"
                  "1003,1,2026-02-02,12.00,refunded\n")
df = pd.read_csv(csv, parse_dates=["order_date"])
print(pd.__version__, df.shape)
print(df.dtypes.astype(str).to_dict())
print(df.isna().sum().to_dict(), df["user_id"].nunique())

a = pd.Series({"x": 1, "y": 2})
b = pd.Series({"y": 10, "z": 5})
print((a + b).to_dict())                    # aligned on labels, gaps -> NaN
print(a.add(b, fill_value=0).to_dict())
```

```text
3.1.1 (3, 5)
{'order_id': 'int64', 'user_id': 'int64', 'order_date': 'datetime64[us]', 'amount': 'float64', 'status': 'str'}
{'order_id': 0, 'user_id': 0, 'order_date': 0, 'amount': 1, 'status': 0} 2
{'x': nan, 'y': 12.0, 'z': nan}
{'x': 1.0, 'y': 12.0, 'z': 5.0}
```

An int column with a blank becomes `float64` (`"Int64"` keeps integers). Too big for memory:
`chunksize=`, `usecols=` (→ §30.5). ex01 profiles with `read_csv` and with `csv` loops: both O(n),
but pandas parses in C into typed columns.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex01_load_inspect.py`.

## 34.2 Selection: `loc`, `iloc`, boolean filters

`loc` selects by **label** (slices include the end), `iloc` by **position**. A boolean mask is
`WHERE`: combine with `&`, `|`, `~`, parenthesising each comparison. NaN comparisons are False,
except `!=` (True), so `df[df.a != 5]` keeps NaN rows (SQL's `a <> 5` drops NULLs).

```python
import pandas as pd

df = pd.DataFrame({"order_id": [1, 2, 3, 4], "amount": [50.0, 80.0, None, 99.0],
                   "status": ["paid", "paid", "paid", "refunded"]})
mask = (df["status"] == "paid") & (df["amount"] >= 60)   # parentheses are required
print(df.loc[mask, "order_id"].tolist())
ranked = df.sort_values("amount", ascending=False)
print(ranked.loc[0, "order_id"], ranked.iloc[0]["order_id"])   # label 0 vs position 0
df.loc[df["status"] == "refunded", "amount"] = 0.0            # one .loc call: works
df[df["status"] == "paid"]["amount"] = -1.0                   # chained: no effect (warns)
print(df["amount"].tolist())
```

```text
[2]
1 4
[50.0, 80.0, nan, 0.0]
```

The chained line warns `ChainedAssignmentError` on stderr: under copy-on-write `df[mask]` is a new
object (aliasing → §7.2). Masks are O(n); `isin(list)` is O(n + k). ex02 checks masks against SQLite.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex02_selection_filters.py`.

## 34.3 Missing data handling

| Question | pandas | SQL |
|---|---|---|
| Test for missing | `isna()`; `x == np.nan` is always False | `IS NULL`; `= NULL` is never true |
| Sum of an all-missing group | `0.0` (`min_count=0`) | `NULL` (`TOTAL()` gives 0.0 in SQLite) |
| Count non-missing / all rows | `count()` / `size` | `COUNT(col)` / `COUNT(*)` |
| Missing group key | dropped unless `dropna=False` | kept as a NULL group |
| Missing join key | **NaN matches NaN** | NULL matches nothing |

ex03 and ex05 check these against SQLite. Impute per group in one O(n) pass,
`s.fillna(df.groupby("user_id")["amount"].transform("median"))`, not a filter per missing row
(O(n·m)). Say whether missing means "zero" or "unknown". A `sqlite3` `with` block commits (or
rolls back) but does not close, so the listings use `contextlib.closing`.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex03_missing_data.py`.

## 34.4 `groupby`, aggregation, `transform`

Split-apply-combine: rows are hashed by key (O(n)), each group is reduced, and with the default
`sort=True` the g keys are sorted (O(g log g)). `agg` returns **one row per group** (`GROUP BY`);
`transform` returns **one value per input row** (`SUM(x) OVER (PARTITION BY k)`).

**Worked problem: country scorecard (ex04).** Per country: paid revenue, orders, distinct buyers,
average order value, and each buyer's revenue share. Duplicates count once; missing country = `"unknown"`.

Ladder: (1) dict-of-lists loops, O(n) in Python objects; (2) `groupby().apply(lambda g: pd.Series(...))`,
O(n) plus a Python call per group; (3) named aggregation + `transform`, O(n + g log g) in C. Same
big-O: move up for constant factors and flat columns.

```python
import numpy as np
import pandas as pd

users = pd.DataFrame({"user_id": [1, 2, 3, 4], "country": ["DE", "DE", None, "US"]})
orders = pd.DataFrame({"order_id": [10, 11, 12, 13, 14, 15, 15],
                       "user_id": [1, 1, 2, 3, 4, 4, 4],
                       "amount": [30.0, 10.0, np.nan, 5.0, 50.0, 7.0, 7.0],
                       "status": ["paid"] * 4 + ["refunded", "paid", "paid"]})


def country_summary(users, orders):
    paid = orders.drop_duplicates().query("status == 'paid'")
    df = paid.merge(users, on="user_id")                     # inner join
    df["country"] = df["country"].fillna("unknown")
    g = df.groupby("country", as_index=False).agg(
        revenue=("amount", "sum"), orders=("order_id", "size"),
        priced=("amount", "count"), buyers=("user_id", "nunique"))
    g["aov"] = (g["revenue"] / g.pop("priced")).round(2)
    per_user = df.groupby(["country", "user_id"])["amount"].sum()
    share = per_user / per_user.groupby("country").transform("sum")
    return (g.sort_values(["revenue", "country"], ascending=[False, True]),
            share.round(3))


summary, share = country_summary(users, orders)
print(summary.to_string(index=False))
print(share.to_dict())
```

```text
country  revenue  orders  buyers  aov
     DE     40.0       3       2 20.0
     US      7.0       1       1  7.0
unknown      5.0       1       1  5.0
{('DE', 1): 1.0, ('DE', 2): 0.0, ('US', 4): 1.0, ('unknown', 3): 1.0}
```

SQL: a `SELECT DISTINCT` paid CTE, then `GROUP BY country`; share =
`revenue / SUM(revenue) OVER (PARTITION BY country)`. Tests check pandas, SQL and loops agree.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex04_groupby_transform.py`.

**Edge cases:** NaN amount (an order, but not in the AOV denominator: `size` vs `count`); duplicate
row; refunds; NULL country; revenue ties (second sort key); all-NaN group (SQL `SUM` is NULL, so use
`TOTAL`). **Wrong-but-tempting:** `groupby().mean()` over text columns raises (pandas ≥ 2:
`numeric_only=False`); `agg("count")` to count orders skips NaN. **Follow-ups:** top-2 buyers with
ties (ex11); share per country and month; countries with no orders (left join from users).

## 34.5 Merge, join, concat (SQL equivalents)

| pandas | SQL | Note |
|---|---|---|
| `a.merge(b, on="k")` | `INNER JOIN` | default `how="inner"` |
| `how="left"` / `"right"` / `"outer"` | `LEFT` / `RIGHT` / `FULL OUTER JOIN` | |
| `indicator=True`, keep `"left_only"` | `LEFT JOIN ... WHERE b.k IS NULL` | anti join |
| `a[a.k.isin(b.k)]` | `WHERE k IN (SELECT k FROM b)` | semi join, no duplication |
| `pd.concat([a, b])` | `UNION ALL` | |

pandas hashes keys: O(n + m + output). The output can be quadratic: a key that appears p times
left and q times right yields p·q rows, so check uniqueness with `validate=`.

```python
import pandas as pd
from pandas.errors import MergeError

users = pd.DataFrame({"user_id": [1, 2, 3]})
orders = pd.DataFrame({"order_id": [10, 11, 12, 13], "user_id": [1, 1, 9, 3]})

left = users.merge(orders, on="user_id", how="left")         # LEFT JOIN
print(left.groupby("user_id")["order_id"].count().to_dict())  # count a column, not rows
tagged = orders.merge(users, on="user_id", how="left", indicator=True)
print(tagged.loc[tagged["_merge"] == "left_only", "order_id"].tolist())   # anti join

tiers = pd.DataFrame({"user_id": [1, 1], "tier": ["gold", "silver"]})    # duplicate key!
print(len(orders.merge(tiers, on="user_id")))                 # 2 orders x 2 tiers = 4 rows
try:
    orders.merge(tiers, on="user_id", validate="many_to_one")
except MergeError as e:
    print("MergeError:", str(e).split(";")[0])
```

```text
{1: 2, 2: 0, 3: 1}
[12]
4
MergeError: Merge keys are not unique in right dataset
```

**Edge cases:** duplicate lookup keys; NaN keys (they match each other, §34.3); `int` vs `str` keys;
unmatched rows; counting rows instead of a column after a left join. Self-joins → §30.7.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex05_merge_joins.py`.

## 34.6 Pivot tables and reshaping (`melt`, `pivot`)

**Long** = one row per (entity, variable); **wide** = one column per variable. `pivot` only
reshapes; `pivot_table` aggregates (default `"mean"`: pass `"sum"`) and fills holes when given
`fill_value=`; `melt` goes back.
SQL needs one `SUM(CASE WHEN month = '2026-01' THEN amount END)` per known column.

```python
import pandas as pd

long = pd.DataFrame({"country": ["DE", "DE", "DE", "US"],
                     "month": ["2026-01", "2026-01", "2026-02", "2026-02"],
                     "amount": [10.0, 5.0, 1.0, 7.0]})
wide = long.pivot_table(index="country", columns="month", values="amount",
                        aggfunc="sum", fill_value=0.0)
print(wide.to_string())
back = wide.reset_index().melt(id_vars="country", var_name="month", value_name="amount")
print(back[back["amount"] > 0].values.tolist())
```

```text
month    2026-01  2026-02
country                  
DE          15.0      1.0
US           0.0      7.0
[['DE', '2026-01', 15.0], ['DE', '2026-02', 1.0], ['US', '2026-02', 7.0]]
```

`long.pivot(...)` on this frame raises `ValueError` (DE/2026-01 repeats). Cost O(n + r·c) for an
r × c result; `stack`/`unstack` are the index-level versions.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex06_pivot_melt.py`.

## 34.7 Time series basics

Parse to `datetime64`, then let the calendar do the work. Missing days are *absent rows*: make
them explicit with `reindex(pd.date_range(...))`, then decide between 0 and NaN.

```python
import pandas as pd

s = pd.DataFrame({"date": pd.to_datetime(["2026-03-02", "2026-03-05", "2026-03-08", "2026-03-09"]),
                  "revenue": [1.0, 2.0, 4.0, 8.0]})
full = s.set_index("date").reindex(pd.date_range("2026-03-02", "2026-03-09", freq="D"))
print(full["revenue"].isna().sum(), "missing days")
weekly = s.groupby(pd.Grouper(key="date", freq="W"))["revenue"].sum()     # weeks end Sunday
print({d.strftime("%a %m-%d"): v for d, v in weekly.items()})
print(s["date"].dt.day_name().tolist(), s["date"].dt.day_of_week.tolist())
print(pd.date_range("2026-01-01", periods=2, freq="ME").strftime("%m-%d").tolist())
```

```text
4 missing days
{'Sun 03-08': 7.0, 'Sun 03-15': 8.0}
['Monday', 'Thursday', 'Sunday', 'Monday'] [0, 3, 6, 0]
['01-31', '02-28']
```

`"W"` = `"W-SUN"`, labelled by the right edge. In SQLite ex07 derives week ends from
`strftime('%w', d)` (Sunday = 0; pandas: Monday = 0).
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex07_time_series.py`.

## 34.8 Window/rolling operations

**Worked problem: per-store window features (ex08).** Running total, previous value and a w-day
moving average per store, with some days missing. Ladder: (1) re-slice the last w values for each
row, O(n·w); (2) `rolling(w)` keeps a running sum, O(n); (3) `rolling("wD")` runs two pointers over
the timestamps, O(n). Only rung 3 is correct across gaps, because "7-day" means calendar days.

```python
import sqlite3
from contextlib import closing

import pandas as pd

days = pd.to_datetime(["2026-03-01", "2026-03-02", "2026-03-03", "2026-03-06", "2026-03-07"])
df = pd.DataFrame({"date": days, "store": "s", "revenue": [1.0, 2.0, 3.0, 10.0, 20.0]})


def window_features(df, w=3):
    df = df.sort_values(["store", "date"]).reset_index(drop=True)
    g = df.groupby("store")["revenue"]
    df["run_total"] = g.cumsum()
    df["prev"] = g.shift(1)                              # previous ROW, not yesterday
    df["rows_w"] = g.transform(lambda s: s.rolling(w).mean())
    df["days_w"] = (df.set_index("date").groupby("store")["revenue"]
                    .rolling(f"{w}D").mean().to_numpy())  # last w CALENDAR days
    return df


out = window_features(df)
print(out.assign(date=out["date"].dt.strftime("%m-%d")).round(2).to_string(index=False))

SQL = """
SELECT date, AVG(revenue) OVER (PARTITION BY store ORDER BY date
                          ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rows_w,
       AVG(revenue) OVER (PARTITION BY store ORDER BY julianday(date)
                          RANGE BETWEEN 2 PRECEDING AND CURRENT ROW) AS days_w
FROM s ORDER BY store, date
"""
with closing(sqlite3.connect(":memory:")) as con:
    df.assign(date=df["date"].dt.strftime("%Y-%m-%d")).to_sql("s", con, index=False)
    for row in con.execute(SQL):
        print(row[0][5:], [None if v is None else round(v, 2) for v in row[1:]])
```

```text
 date store  revenue  run_total  prev  rows_w  days_w
03-01     s      1.0        1.0   NaN     NaN     1.0
03-02     s      2.0        3.0   1.0     NaN     1.5
03-03     s      3.0        6.0   2.0     2.0     2.0
03-06     s     10.0       16.0   3.0     5.0    10.0
03-07     s     20.0       36.0  10.0    11.0    15.0
03-01 [1.0, 1.0]
03-02 [1.5, 1.5]
03-03 [2.0, 2.0]
03-06 [5.0, 10.0]
03-07 [11.0, 15.0]
```

Row and calendar windows diverge after the gap (03-06: 5.0 vs 10.0). At the start, count windows
default to `min_periods=w` (NaN) while SQL averages whatever rows exist. `cumsum` is
`SUM() OVER (... ROWS UNBOUNDED PRECEDING)` and `shift(1)` is `LAG()`; ex08 has all four in SQL
and tests a 7-day, two-store version against SQLite.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex08_rolling_windows.py`.

A time window is (d − w, d] by default; "the 7 days before today" is `rolling("7D", closed="left")`
= `RANGE BETWEEN 7 PRECEDING AND 1 PRECEDING` (ex08 tests that the two agree).
**Wrong-but-tempting:** `rolling(7)` for "7-day"; `df["revenue"].shift(1)` without `groupby`, which
leaks the last north row into south. **Edge cases:** unsorted input; duplicate dates (no frame means
`RANGE`, summing ties); `prev` across a gap is not "yesterday" (§34.7); zero `prev`.
**Follow-ups:** `ewm(alpha=...)`; centred windows (`center=True`; SQL `AND 3 FOLLOWING`).
`RANGE` offsets need SQLite ≥ 3.28; window syntax → §30.9.

## 34.9 Analytical SQL interview questions (cohorts, retention, funnels)

**Worked problem: monthly cohort retention (ex09).** Cohort = signup month. A user is active at
offset k if they have a paid order in calendar month cohort + k. Output: a cohort × k matrix of
active users / cohort size, with NaN where cohort + k is in the future.

Ladder: (1) scan all orders for each cell, O(C·K·n); (2) one pass into `{(cohort, k): set}`, O(n + C·K)
in Python; (3) integer month index + `groupby([c, k]).nunique()` + `unstack`, O(n + C·K) vectorised.
Move up because rung 1 rescans the data C·K times, while rung 3 is one grouped pass that maps to one
SQL `GROUP BY`.

```python
import numpy as np
import pandas as pd

users = pd.DataFrame({"user_id": [1, 2, 3, 4], "signup_date": pd.to_datetime(
    ["2026-01-30", "2026-01-02", "2026-02-10", "2026-02-11"])})
orders = pd.DataFrame({"user_id": [1, 1, 1, 3, 9], "status": "paid", "order_date": pd.to_datetime(
    ["2026-02-01", "2026-02-20", "2026-03-01", "2026-03-05", "2026-01-15"])})


def month_index(s):
    return s.dt.year * 12 + s.dt.month                  # plain ints: no Period objects


def retention(users, orders):
    u = users.assign(c=month_index(users["signup_date"]))
    size = u.groupby("c")["user_id"].nunique()          # from users: non-buyers count
    paid = orders[orders["status"] == "paid"].merge(u, on="user_id")   # drops user 9
    paid["k"] = month_index(paid["order_date"]) - paid["c"]
    active = (paid[paid["k"] >= 0].groupby(["c", "k"])["user_id"].nunique()
              .unstack(fill_value=0))
    last = int(month_index(orders["order_date"]).max())
    ks = range(last - int(size.index.min()) + 1)
    rates = active.reindex(index=size.index, columns=ks, fill_value=0).div(size, axis=0)
    seen = np.add.outer(size.index.to_numpy(), np.array(ks)) <= last
    return rates.where(seen).round(3).assign(size=size)  # NaN = not observable yet


print(retention(users, orders).rename(index=lambda i: f"{(i - 1) // 12}-{(i - 1) % 12 + 1:02d}").to_string())
```

```text
k          0    1    2  size
c                           
2026-01  0.0  0.5  0.5     2
2026-02  0.0  0.5  NaN     2
```

User 1 signed up on 30 Jan and ordered on 1 Feb: offset 1, because this uses calendar months, not
30-day blocks (say which). On the repo data (40 users, 4 cohorts) the 2026-01 cohort row is
0.250, 0.500, 0.375, 0.125, 0.375, 0.375. SQL: CTEs `u` (month index), `sizes` and `act`
(`SELECT DISTINCT c_idx, user_id, k`), then `GROUP BY c_idx, k` (CTEs → §30.8).
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex09_cohort_retention.py`.

**Edge cases:** size from `users` (users 6, 39, 40 never pay); many orders in a month = one active
user; unknown users; orders before signup (k < 0); future NaN vs observed 0.0.
**Wrong-but-tempting:** cohort size counted from orders; 30-day blocks or `Period` subtraction
(offset objects, not ints) for k. **Follow-ups:**
revenue retention; weekly cohorts; "rolling" retention (month k *or later*); significance (→ §35.6).

**The other classics, as patterns:**

| Question | pandas | SQL |
|---|---|---|
| Ordered funnel (ex10) | per step: merge step events onto `t_prev`, keep `ts >= t_prev`, `min` | one CTE per step joined on `e.ts >= prev.t` |
| N-th highest per group, ties shared (ex11) | `rank(method="dense", ascending=False) == n` | `DENSE_RANK() OVER (PARTITION BY g ORDER BY v DESC)` |
| Latest row per key | `sort_values` + `drop_duplicates(keep="last")` | `ROW_NUMBER() ... = 1` |
| Consecutive-day streaks (ex11) | dedupe dates per key; `date - cumcount() days` is constant per run | `julianday(d) - DENSE_RANK()` (duplicates would split a run under `ROW_NUMBER`) |

Rank methods: `"first"`/`"min"`/`"dense"` = `ROW_NUMBER`/`RANK`/`DENSE_RANK`. **Wrong-but-tempting
funnels:** an unordered count (distinct users per event) ignores time: the repo data has 15
purchasers, but only 13 purchase after checkout. Comparing each step's *first* timestamp is also
wrong: cart 09:00, view 09:05, cart 09:10 converted, but the shortcut says no. Each pattern costs
O(n log n) at worst (the sort).
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex10_funnel_conversion.py`,
`chapters/ch34_pandas_sql_analysis/solutions/ex11_sql_classics.py`.

## 34.10 Practice set

The exercises below. Drill ex04, ex08, ex09, ex11 at 25 min each.

## Interviewer's view

- **Rewarded:** grain, NULL and tie rules first; vectorised code, deterministic sorts; sanity
  checks (row counts around joins); the SQL for each step.
- **Penalised:** `iterrows`; chained assignment; counting rows after a left join; `pivot_table`
  with the default mean; joins that silently multiply rows.
- **Strong signal:** checking a tiny hand-computed frame before the full data.

## Exercises

All in `chapters/ch34_pandas_sql_analysis/`.

| ID | Title | Tier | Pattern |
|---|---|---|---|
| ex01 | Load, type and profile a CSV | ★ | `read_csv` dtypes, alignment |
| ex02 | Selection with loc, iloc and masks | ★ | mask = `WHERE`, copy-on-write |
| ex03 | Missing data: NaN vs NULL | ★ | `transform("median")`, `dropna=False` |
| ex04 | Country scorecard | ★ | named `agg`, `transform` |
| ex05 | Joins: inner, left, anti, duplicate keys | ★ | `indicator=`, `validate=` |
| ex06 | Pivot tables and melt | ◆ | `pivot_table`, `CASE WHEN` |
| ex07 | Time series: gaps, weeks, weekdays | ★ | `reindex`, `Grouper(freq="W")` |
| ex08 | Rolling, running and lag features | ★ | `rolling(7)` vs `rolling("7D")` |
| ex09 | Monthly cohort retention | ★ | month offset + `unstack` |
| ex10 | Ordered conversion funnel | ◆ | per-step merge + `min` |
| ex11 | Nth highest, latest row, streaks | ◆ | `DENSE_RANK`, gaps-and-islands |

## Checkpoint quiz

1. `df[df.x > 0]["y"] = 0` runs without an exception in pandas 3. What happens to `df`?
2. A group's values are all NaN. What do pandas `sum()` and SQL `SUM()` return?
3. Joining 1,000 orders to a lookup gives 1,240 rows. Why, and how do you prevent it?
4. When do `rolling(7)` and `rolling("7D")` differ?
5. Why must cohort size come from the users table?

<details>
<summary>Answers</summary>

1. Nothing (copy-on-write). Use `df.loc[df.x > 0, "y"] = 0`.
2. pandas `0.0` (`min_count=1` gives NaN); SQL `NULL` (SQLite `TOTAL()` gives 0.0).
3. Duplicate lookup keys multiply rows: `validate="many_to_one"` raises `MergeError`; dedupe first.
4. When days are missing or duplicated: 7 rows no longer span 7 calendar days.
5. Non-buyers are in the cohort; counting from orders inflates retention.

</details>

## Summary card

- pandas 3: `str` dtype, `datetime64[us]`, copy-on-write; read with `dtype=`/`parse_dates=`.
- Labels align; `loc` = labels (inclusive), `iloc` = positions; one `.loc[mask, col] =`.
- NaN: all-NaN `sum` = 0.0 (SQL NULL); `groupby` drops NaN keys; `merge` matches them (SQL doesn't).
- `agg` = one row per group (`GROUP BY`); `transform` = one per row (`OVER (PARTITION BY)`).
- `merge`: hash join, O(n + m + output); `indicator=` anti joins; `validate=` against blow-ups.
- `pivot_table(aggfunc="sum", fill_value=0)` ↔ `melt`; SQL pivots with `SUM(CASE WHEN ...)`.
- Sort, then per-group `cumsum`/`shift`/`rolling`; count and time windows differ across gaps.
- Ranks: first/min/dense = `ROW_NUMBER`/`RANK`/`DENSE_RANK`.
