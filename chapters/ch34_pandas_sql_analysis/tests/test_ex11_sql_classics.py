from contextlib import closing
import random
import sqlite3

import numpy as np
import pandas as pd
import pytest


@pytest.mark.parametrize("vals, n, expected", [
    ([5, 5, 3], 2, 3),            # ties share a rank
    ([5, 5], 2, None),            # fewer distinct values than n
    ([7], 1, 7),
    ([1, np.nan, 2], 2, 1),       # NaN ignored
    ([4, 9, 9, 8, 4], 3, 4),
])
def test_nth_highest(load, vals, n, expected):
    m = load("ex11_sql_classics")
    df = pd.DataFrame({"g": ["a"] * len(vals), "v": [float(v) for v in vals]})
    assert m.nth_highest(df, "g", "v", n)["a"] == expected
    with closing(sqlite3.connect(":memory:")) as conn:
        df.to_sql("t", conn, index=False)
        assert m.sql_nth_highest(conn, n)["a"] == expected


def test_nth_random(load):
    m = load("ex11_sql_classics")
    rng = random.Random(11)
    for _ in range(50):
        k = rng.randint(1, 12)
        df = pd.DataFrame({"g": [rng.choice("xyz") for _ in range(k)],
                           "v": [float(rng.randint(1, 4)) for _ in range(k)]})
        n = rng.randint(1, 3)
        assert m.nth_highest(df, "g", "v", n) == m.brute_force_nth_highest(df, "g", "v", n)


def test_latest_ties_and_duplicates(load):
    m = load("ex11_sql_classics")
    # tied 01-05 rows appear with the LARGER order_id first, so sorting by date alone picks 2
    orders = pd.DataFrame({"order_id": [1, 3, 2, 4, 4], "user_id": [1, 1, 1, 2, 2],
                           "order_date": pd.to_datetime(["2026-01-02", "2026-01-05", "2026-01-05",
                                                         "2026-01-01", "2026-01-01"])})
    assert m.latest_per_user(orders) == {1: 3, 2: 4}
    with closing(sqlite3.connect(":memory:")) as conn:
        orders.assign(order_date=orders["order_date"].dt.strftime("%Y-%m-%d")).to_sql("orders", conn, index=False)
        assert m.sql_latest_per_user(conn) == {1: 3, 2: 4}


def test_latest_tie_order_both_ways(load):
    m = load("ex11_sql_classics")
    # same-date ties inserted [3, 2] for user 1 and [2, 3] for user 2: only "order_id DESC" gets both
    orders = pd.DataFrame({"order_id": [3, 2, 2, 3], "user_id": [1, 1, 2, 2],
                           "order_date": pd.to_datetime(["2026-01-05"] * 4)})
    orders = orders.assign(order_id=orders["order_id"] + 10 * orders["user_id"])   # unique ids
    expected = {1: 13, 2: 23}
    assert m.latest_per_user(orders) == expected
    with closing(sqlite3.connect(":memory:")) as conn:
        orders.assign(order_date=orders["order_date"].dt.strftime("%Y-%m-%d")).to_sql("orders", conn, index=False)
        assert m.sql_latest_per_user(conn) == expected


def test_streaks(load):
    m = load("ex11_sql_classics")
    days = ["2026-03-01", "2026-03-02", "2026-03-04", "2026-03-05", "2026-03-06", "2026-03-08"]
    sales = pd.DataFrame({"date": pd.to_datetime(days + ["2026-03-01", "2026-03-03"]),
                          "store": ["a"] * 6 + ["b", "b"], "revenue": 1.0})
    expected = {"a": ("2026-03-04", 3), "b": ("2026-03-01", 1)}     # b ties: earliest run wins
    assert m.longest_streak(sales) == expected == m.brute_force_streak(sales)
    with closing(sqlite3.connect(":memory:")) as conn:
        sales.assign(date=sales["date"].dt.strftime("%Y-%m-%d")).to_sql("sales", conn, index=False)
        assert m.sql_longest_streak(conn) == expected


def test_real_streaks(load):
    m = load("ex11_sql_classics")
    sales = pd.read_csv(m.DATA / "daily_sales.csv", parse_dates=["date"])
    assert m.longest_streak(sales) == {"north": ("2026-03-12", 20), "south": ("2026-03-01", 20)}
