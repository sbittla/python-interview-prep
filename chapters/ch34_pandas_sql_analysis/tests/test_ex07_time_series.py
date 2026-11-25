from contextlib import closing
import sqlite3

import pandas as pd


def small():
    return pd.DataFrame({
        "date": pd.to_datetime(["2026-03-02", "2026-03-05", "2026-03-08", "2026-03-09", "2026-03-04"]),
        "store": ["a", "a", "a", "a", "b"],
        "revenue": [1.0, 2.0, 4.0, 8.0, 5.0],
    })


def test_missing_and_complete_small(load):
    m = load("ex07_time_series")
    s = small()
    assert m.missing_days(s) == {"a": ["2026-03-03", "2026-03-04", "2026-03-06", "2026-03-07"], "b": []}
    assert m.missing_days(s) == m.brute_force_missing(s)
    full = m.complete_daily(s)
    assert len(full) == 8 + 1
    assert full.loc[full["store"] == "a", "revenue"].tolist() == [1.0, 0, 0, 2.0, 0, 0, 4.0, 8.0]
    assert int(full["filled"].sum()) == 4


def test_weekly_bins_end_sunday(load):
    m = load("ex07_time_series")
    w = m.weekly_totals(small())
    # Mon 2 .. Sun 8 is one week; Mon 9 starts the next
    assert w.values.tolist() == [["a", "2026-03-08", 7.0], ["a", "2026-03-15", 8.0], ["b", "2026-03-08", 5.0]]
    with closing(sqlite3.connect(":memory:")) as conn:
        small().assign(date=lambda d: d["date"].dt.strftime("%Y-%m-%d")).to_sql("sales", conn, index=False)
        assert m.sql_weekly_totals(conn).equals(w)


def test_weekday_weekend(load):
    m = load("ex07_time_series")
    extra = pd.DataFrame({"date": pd.to_datetime(["2026-03-07"]), "store": ["b"], "revenue": [9.0]})
    s = pd.concat([small(), extra], ignore_index=True)
    # a: Mon 1, Thu 2, Sun 4, Mon 8; b: Wed 5, Sat 9
    assert m.weekday_vs_weekend(s) == {"a": (round(11 / 3, 2), 4.0), "b": (5.0, 9.0)}


def test_real_data(load):
    m = load("ex07_time_series")
    sales = m.load_sales()
    assert m.missing_days(sales) == {"north": ["2026-03-10", "2026-03-11"], "south": ["2026-03-21"]}
    w = m.weekly_totals(sales)
    assert abs(w["revenue"].sum() - sales["revenue"].sum()) < 0.05
    with closing(sqlite3.connect(":memory:")) as conn:
        sales.assign(date=sales["date"].dt.strftime("%Y-%m-%d")).to_sql("sales", conn, index=False)
        assert m.sql_weekly_totals(conn).equals(w)
