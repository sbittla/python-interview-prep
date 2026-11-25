# Chapter 34. Pandas and SQL for Analysis

★ Core · Tracks M L · Study time ≈ 6 h · Prerequisites: §30.6–§30.10 (SQL, `sqlite3`), §33.4–§33.5 (vectorising, axis aggregations)

**Learning objectives**

- Load, type, filter and reshape tabular data in pandas without Python loops.
- Translate between pandas and SQL: mask ↔ `WHERE`, `groupby` ↔ `GROUP BY`, `transform` ↔
  `OVER (PARTITION BY)`, `merge` ↔ `JOIN`, `rolling` ↔ `ROWS BETWEEN`.
- Handle NaN/NULL, duplicate join keys, missing days and ties on purpose.
- Solve the analytics round classics: cohort retention, funnels, top-N per group, streaks.

> **Recognise it.** "Here is a CSV / table, compute per-X metrics"; "monthly", "per user",
> "share of total", "rolling 7-day", "retention", "conversion", "second highest", "consecutive
> days". Small data you can see (< 10⁶ rows) → pandas; "write the query" → SQL. Strong candidates
> state the NULL rule, the tie rule and the grain (one row per what?) before coding.

**Version baseline.** Everything here ran on **pandas 3.1.1**, NumPy 2.5.5, SQLite 3.50.4 and
CPython 3.13 (no pyarrow installed). pandas 3 changed three things interviewers now ask about:

| pandas 3 behaviour | pandas 2.x default | Consequence |
|---|---|---|
| Copy-on-write always on | opt-in | chained assignment never writes; `ChainedAssignmentError` warning |
| Text columns get dtype `str` (pyarrow-backed if installed, else Python) | `object` | test `is_string_dtype`, not `== object` |
| Parsed datetimes default to `datetime64[us]` | `[ns]` | don't hard-code the unit |

Aliases `"M"`/`"H"` were replaced by `"ME"`/`"h"` in 2.2 (plain `"M"` raises in 3.1); in 3.1 even
`.dt.dayofweek` warns as deprecated (use `.dt.day_of_week`).

## 34.1 Series and DataFrames; reading data

A **Series** is a 1-D array plus an index of labels; a **DataFrame** is a dict of Series that
share one index. Arithmetic **aligns on labels**, not positions. Pass dtypes and `parse_dates`
when reading, so later steps compare numbers and timestamps, not strings.

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

An int column with a blank becomes `float64`; use `"Int64"` (nullable) to keep integers. `df["a"]`
is a Series, `df[["a"]]` a DataFrame. For files that don't fit in memory: `chunksize=`, `usecols=`
(→ §30.5). ex01 profiles `orders.csv` with `read_csv` and again with the `csv` module (O(n) both;
the pandas pass runs in C and yields typed columns).
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex01_load_inspect.py`.

## 34.2 Selection: `loc`, `iloc`, boolean filters

`loc` selects by **label** (slices include the end), `iloc` by **position** (end excluded). A
boolean mask is SQL's `WHERE`; combine with `&`, `|`, `~` and parenthesise each comparison
(`&` binds tighter than `>=`). Comparisons with NaN are False, so NaN rows drop out silently.

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

The chained line prints `ChainedAssignmentError` to stderr: under copy-on-write `df[mask]` is a
new object, so writing into it never reaches `df` (aliasing basics → §7.2). Masks are O(n);
`isin(list)` hashes the list, O(n + k). ex02 cross-checks a mask against the same `WHERE` in SQLite.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex02_selection_filters.py`.

## 34.3 Missing data handling

| Question | pandas | SQL |
|---|---|---|
| Test for missing | `isna()`; `x == np.nan` is always False | `IS NULL`; `= NULL` is never true |
| Sum of an all-missing group | `0.0` (`min_count=0`) | `NULL` (`TOTAL()` gives 0.0 in SQLite) |
| Count non-missing / all rows | `count()` / `size` | `COUNT(col)` / `COUNT(*)` |
| Missing group key | dropped unless `dropna=False` | kept as a NULL group |
| Missing join key | **NaN matches NaN** | NULL matches nothing |

```python
import sqlite3
from contextlib import closing

import numpy as np
import pandas as pd

g = pd.DataFrame({"k": ["a", "a", "b", None], "v": [1.0, np.nan, np.nan, 3.0]})
print(g.groupby("k")["v"].agg(["sum", "count", "size"]).to_dict("index"))
print(g.groupby("k", dropna=False)["v"].sum().to_dict())
print(g["v"].sum(), g.loc[g["k"] == "b", "v"].sum(min_count=1), (g["v"] == np.nan).any())
with closing(sqlite3.connect(":memory:")) as con:
    g.to_sql("g", con, index=False)
    print(con.execute("SELECT k, SUM(v), COUNT(v), COUNT(*) FROM g GROUP BY k ORDER BY k").fetchall())
```

```text
{'a': {'sum': 1.0, 'count': 1, 'size': 2}, 'b': {'sum': 0.0, 'count': 0, 'size': 1}}
{'a': 1.0, 'b': 0.0, nan: 3.0}
4.0 nan False
[(None, 3.0, 1, 1), ('a', 1.0, 1, 2), ('b', None, 0, 1)]
```

Impute per group in one pass: `s.fillna(df.groupby("user_id")["amount"].transform("median"))`,
then fall back to the global median, O(n) hashing versus O(n·m) for a filter per missing row
(ex03). Decide out loud whether a missing value means "zero" or "unknown"; it changes every mean.
`sqlite3.connect` used as a `with` block only commits, so close with `contextlib.closing`.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex03_missing_data.py`.

## 34.4 `groupby`, aggregation, `transform`

Split-apply-combine: rows are hashed by key (O(n)), each group is reduced, and with the default
`sort=True` the g group keys are sorted (O(g log g)). `agg` returns **one row per group** (SQL
`GROUP BY`); `transform` returns **one value per input row** (SQL `SUM(x) OVER (PARTITION BY k)`).

**Worked problem: country scorecard (ex04).** Per country: paid revenue, paid orders, distinct
buyers, average order value; and each buyer's share of their country's revenue. Duplicated rows
must count once; missing country is `"unknown"`.

Ladder: (1) dict-of-lists loops, O(n) but Python objects throughout; (2) `groupby().apply(lambda g:
pd.Series(...))`, still O(n) but a Python call and a Series per group; (3) named aggregation +
`transform`, O(n + g log g) in C. Move up for constant factors and flat output; the big-O is the same.

```python
import sqlite3
from contextlib import closing

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

SQL = """
WITH paid AS (SELECT DISTINCT o.*, COALESCE(u.country, 'unknown') AS country
              FROM orders o JOIN users u USING (user_id) WHERE o.status = 'paid')
SELECT country, TOTAL(amount) AS revenue, COUNT(*) AS orders,
       COUNT(DISTINCT user_id) AS buyers, ROUND(TOTAL(amount) / COUNT(amount), 2) AS aov
FROM paid GROUP BY country ORDER BY revenue DESC, country
"""
with closing(sqlite3.connect(":memory:")) as con:
    users.to_sql("users", con, index=False)
    orders.to_sql("orders", con, index=False)
    print(con.execute(SQL).fetchall())
```

```text
country  revenue  orders  buyers  aov
     DE     40.0       3       2 20.0
     US      7.0       1       1  7.0
unknown      5.0       1       1  5.0
{('DE', 1): 1.0, ('DE', 2): 0.0, ('US', 4): 1.0, ('unknown', 3): 1.0}
[('DE', 40.0, 3, 2, 20.0), ('US', 7.0, 1, 1, 7.0), ('unknown', 5.0, 1, 1, 5.0)]
```

On the repo data (87 orders) the same code yields US 1650.20 from 28 orders, and the tests assert
pandas, SQL and the loop version agree. → repo:
`chapters/ch34_pandas_sql_analysis/solutions/ex04_groupby_transform.py`.

**Edge cases:** the NaN amount (order counted, AOV denominator excludes it: `size` vs `count`);
an exact duplicate row; refunded rows; NULL country; ties on revenue (secondary sort key); a
group whose amounts are all NaN (pandas 0.0, SQL `SUM` NULL, so the SQL uses `TOTAL`).
**Wrong-but-tempting:** `df.groupby("country").mean()` over every column raises on text
columns (pandas ≥ 2 defaults `numeric_only=False`); `agg("count")` to count orders (skips NaN);
merging the country total back with `merge` instead of `transform` (works, one more join).
**Follow-ups:** top-2 buyers per country with ties (dense rank, ex11); share per country and
month (two keys); revenue per country *including countries with no orders* (left join from users).

## 34.5 Merge, join, concat (SQL equivalents)

| pandas | SQL | Note |
|---|---|---|
| `a.merge(b, on="k")` | `INNER JOIN` | default `how="inner"` |
| `how="left"` / `"right"` / `"outer"` | `LEFT` / `RIGHT` / `FULL OUTER JOIN` | |
| `indicator=True`, keep `"left_only"` | `LEFT JOIN ... WHERE b.k IS NULL` | anti join |
| `a[a.k.isin(b.k)]` | `WHERE k IN (SELECT k FROM b)` | semi join, no duplication |
| `pd.concat([a, b])` | `UNION ALL` | stacks rows; `drop_duplicates()` ≈ `UNION` |
| `a.join(b)` | join on the index | |

pandas hashes keys: O(n + m + output). Output can be quadratic: a key appearing p times on the
left and q times on the right yields p·q rows, so check uniqueness with `validate=`.

```python
import numpy as np
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

a = pd.DataFrame({"k": ["x", np.nan], "a": [1, 2]})
b = pd.DataFrame({"k": ["x", np.nan], "b": [3, 4]})
print(len(a.merge(b, on="k")))       # 2: pandas matches NaN to NaN; SQL NULL = NULL never matches
```

```text
{1: 2, 2: 0, 3: 1}
[12]
4
MergeError: Merge keys are not unique in right dataset
2
```

**Edge-case checklist for joins:** duplicate keys on the "lookup" side; NaN keys; keys of
different dtypes (`int` vs `str` "1"); unmatched rows on either side; counting rows instead of a
non-null column after a left join. SQL join types and self-joins → §30.7.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex05_merge_joins.py`.

## 34.6 Pivot tables and reshaping (`melt`, `pivot`)

**Long** format has one row per (entity, variable); **wide** has one column per variable.
`pivot` only reshapes and raises on a repeated (index, column) pair; `pivot_table` aggregates
(default `aggfunc="mean"`, so pass `"sum"`) and fills holes; `melt` goes back to long. In SQL a pivot
is one `SUM(CASE WHEN month = '2026-01' THEN amount END)` per column, so you must know the columns
up front; pivoting in pandas after a long query is often easier.

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
try:
    long.pivot(index="country", columns="month", values="amount")
except ValueError as e:
    print("pivot:", str(e))
```

```text
month    2026-01  2026-02
country                  
DE          15.0      1.0
US           0.0      7.0
[['DE', '2026-01', 15.0], ['DE', '2026-02', 1.0], ['US', '2026-02', 7.0]]
pivot: Index contains duplicate entries, cannot reshape
```

Cost O(n + r·c) for r rows × c columns of output. `stack`/`unstack` do the same on index levels.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex06_pivot_melt.py`.

## 34.7 Time series basics

Parse to `datetime64`, then use the calendar instead of string arithmetic. Missing days are
*absent rows*; make them explicit with `reindex(pd.date_range(...))`, then decide 0 or NaN.

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

`"W"` means `"W-SUN"`: bins are labelled by their right edge. SQLite has no week type: ex07 computes
week ends with `date(d, '+N days')` from `strftime('%w', d)` (Sunday = 0, unlike pandas' Monday = 0).
Time zones: `tz_localize`, then `tz_convert`; never mix naive and aware stamps.
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex07_time_series.py`.

## 34.8 Window/rolling operations

**Worked problem: per-store window features (ex08).** Running total, previous value, and a w-day
moving average, per store, when some days are missing. Ladder: (1) re-slice the last w values for
every row, O(n·w); (2) `rolling(w)` keeps a running sum (add the new value, drop the old),
O(n); (3) `rolling("wD", on=date)` does the same with two pointers over timestamps, O(n), and is
the only rung correct across gaps. Move up because "7-day average" means calendar days.

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
SELECT date, SUM(revenue) OVER (PARTITION BY store ORDER BY date) AS run_total,
       LAG(revenue) OVER (PARTITION BY store ORDER BY date) AS prev,
       AVG(revenue) OVER (PARTITION BY store ORDER BY date
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
03-01 [1.0, None, 1.0, 1.0]
03-02 [3.0, 1.0, 1.5, 1.5]
03-03 [6.0, 2.0, 2.0, 2.0]
03-06 [16.0, 3.0, 5.0, 10.0]
03-07 [36.0, 10.0, 11.0, 15.0]
```

Row and calendar windows diverge right after the gap (03-06: 5.0 vs 10.0). The `rows_w` column also
differs at the start: count windows default to `min_periods=w` (NaN), SQL averages whatever rows
exist; ex08 adds `CASE WHEN COUNT(*) OVER w = 7` to match. The repo version runs on two stores
and a 7-day window and the tests check it against SQLite. → repo:
`chapters/ch34_pandas_sql_analysis/solutions/ex08_rolling_windows.py`.

**Edge cases:** unsorted input (sort first); windows leaking across stores (always group);
duplicate dates (`ORDER BY date` without a frame defaults to `RANGE`, which sums tied rows
together); `prev` across a gap is not "yesterday" (reindex first, §34.7); division by a zero `prev`.
**Follow-ups:** `ewm(alpha=...)`; centred windows (`center=True`; SQL `... AND 3 FOLLOWING`);
`RANGE` offsets need SQLite ≥ 3.28. Window-function syntax → §30.9.

## 34.9 Analytical SQL interview questions (cohorts, retention, funnels)

**Worked problem: monthly cohort retention (ex09).** Cohort = signup month. A user is active at
offset k if they have a paid order in calendar month cohort + k. Output: cohort × k matrix of
active users / cohort size; NaN where cohort + k is in the future.

Ladder: (1) for each cell, scan all orders: O(C·K·n); (2) one pass into `{(cohort, k): set}`, then
fill the grid: O(n + C·K) in Python; (3) integer month index, `groupby([c, k]).nunique()` and
`unstack`: O(n + C·K) vectorised; dividing by the size Series broadcasts by index alignment.

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

User 1 signed up 30 Jan and ordered 1 Feb: month offset 1, not 0 (calendar months, not 30-day
blocks: state which you use). On the repo data (40 users, four cohorts) the matrix is:

```text
         size      0      1      2      3      4      5
cohort                                                 
2026-01     8  0.250  0.500  0.375  0.125  0.375  0.375
2026-02    10  0.300  0.600  0.400  0.600  0.300    NaN
2026-03     8  0.500  0.500  0.750  0.375    NaN    NaN
2026-04    14  0.357  0.643  0.357    NaN    NaN    NaN
```

The SQL version is three CTEs (`u` with the month index, `sizes`, `act` with `SELECT DISTINCT
c_idx, user_id, k`), then `COUNT(user_id) ... GROUP BY c_idx, k` (CTEs → §30.8).
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex09_cohort_retention.py`.

**Edge cases:** cohort size from `users`, not `orders` (users 6, 39, 40 never pay); several orders
in one month = one active user; orders from unknown users; orders before signup (k < 0); future
cells NaN vs observed-zero 0.0. **Follow-ups:** revenue retention; weekly cohorts; "rolling"
retention (active in month k *or later*); significance of a retention change (→ §35.6).

**The other classics, as patterns:**

| Question | pandas | SQL |
|---|---|---|
| Ordered funnel (ex10) | per step: merge step events onto `t_prev`, keep `ts >= t_prev`, `min` | one CTE per step joined on `e.ts >= prev.t` |
| N-th highest per group, ties shared (ex11) | `rank(method="dense", ascending=False) == n` | `DENSE_RANK() OVER (PARTITION BY g ORDER BY v DESC)` |
| Latest row per key | `sort_values` + `drop_duplicates(keep="last")` | `ROW_NUMBER() ... = 1` |
| Consecutive-day streaks (ex11) | `date - cumcount() days` is constant per run | `julianday(d) - ROW_NUMBER()` |
| Top-N per group | `sort_values` + `groupby().head(n)` | `ROW_NUMBER() <= n` |

Rank method map: `"first"` = `ROW_NUMBER`, `"min"` = `RANK`, `"dense"` = `DENSE_RANK`. The funnel's
**wrong-but-tempting** shortcut takes each step's *first* timestamp and requires t_view ≤ t_cart:
a user with cart 09:00, view 09:05, cart 09:10 converted, but the shortcut says no. On the repo
data, 15 users ever purchase but only 13 do so after checkout. Each problem is O(n log n) at worst (the sort).
→ repo: `chapters/ch34_pandas_sql_analysis/solutions/ex10_funnel_conversion.py`,
`chapters/ch34_pandas_sql_analysis/solutions/ex11_sql_classics.py`.

## 34.10 Practice set

The eleven exercises below are the practice set: each has a pandas solution, a SQLite query,
a brute-force rung and tests that cross-check all three. For timed practice, do ex04, ex08, ex09
and ex11 in 25 minutes each, first in pandas, then in SQL.

## Interviewer's view

- **Rewarded:** stating the grain and the NULL/tie rules first; vectorised code with a sort
  key for determinism; checking the result (row counts before/after a join, shares sum to 1);
  knowing the SQL equivalent of each pandas step.
- **Penalised:** `iterrows` loops; chained assignment; counting rows after a left join;
  `pivot_table` with the default mean; joins that silently multiply rows.
- **Strong signal:** you sanity-check against a tiny hand-computed frame before running on
  the full data.

## Exercises

All in `chapters/ch34_pandas_sql_analysis/` (statements, ladders, SQL and tests in the repo).

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
3. You join 1,000 orders to a lookup and get 1,240 rows. What happened, and how do you prevent it?
4. When do `rolling(7)` and `rolling("7D")` give different answers?
5. Why must cohort size come from the users table?

<details>
<summary>Answers</summary>

1. Nothing: copy-on-write makes `df[mask]` a new object; pandas warns `ChainedAssignmentError`.
   Use `df.loc[df.x > 0, "y"] = 0`.
2. pandas `0.0` (`min_count=0`; pass `min_count=1` for NaN); SQL `NULL` (SQLite `TOTAL()` gives 0.0).
3. The lookup has duplicate keys, so each match multiplies rows. Use
   `validate="many_to_one"` (raises `MergeError`) or deduplicate the lookup first.
4. When days are missing (or duplicated): 7 rows then span more than 7 calendar days.
5. Users who never order are still in the cohort; counting from orders inflates retention.

</details>

## Summary card

- Read with `dtype=`/`parse_dates=`; pandas 3: `str` dtype, `datetime64[us]`, copy-on-write always.
- Arithmetic aligns on labels; `loc` = labels (inclusive), `iloc` = positions; one `.loc[mask, col] =`.
- NaN: `isna()`; `sum` of all-NaN = 0.0 (SQL NULL); `groupby` drops NaN keys unless `dropna=False`;
  `merge` matches NaN keys (SQL doesn't).
- `agg` = one row per group (`GROUP BY`); `transform` = one per row (`OVER (PARTITION BY)`).
- `merge`: hash join O(n + m + output); `indicator=` for anti joins; `validate=` against duplication.
- `pivot_table(aggfunc="sum", fill_value=0)` ↔ `melt`; SQL pivots with `SUM(CASE WHEN ...)`.
- Missing days are missing rows: `reindex(date_range)`; `"W"` = weeks ending Sunday; `"ME"` month end.
- `cumsum`/`shift`/`rolling` per group after sorting; count vs time windows differ across gaps.
- Retention = cohort size from users, integer month offsets, `nunique`, NaN for future cells.
- Ranks: first/min/dense = `ROW_NUMBER`/`RANK`/`DENSE_RANK`; streaks: date − row number.
