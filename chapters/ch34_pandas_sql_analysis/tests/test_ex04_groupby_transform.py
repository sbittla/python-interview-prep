from contextlib import closing

import numpy as np
import pandas as pd


def small():
    users = pd.DataFrame({"user_id": [1, 2, 3, 4], "country": ["DE", "DE", None, "US"]})
    orders = pd.DataFrame({
        "order_id": [10, 11, 12, 13, 14, 15, 15],
        "user_id": [1, 1, 2, 3, 4, 4, 4],
        "order_date": pd.to_datetime(["2026-01-01"] * 7),
        "amount": [30.0, 10.0, np.nan, 5.0, 50.0, 7.0, 7.0],
        "status": ["paid", "paid", "paid", "paid", "refunded", "paid", "paid"],
    })
    return users, orders


def test_summary_small(load):
    m = load("ex04_groupby_transform")
    s = m.country_summary(*small())
    assert list(s.columns) == ["country", "revenue", "orders", "buyers", "aov"]
    assert s.values.tolist() == [
        ["DE", 40.0, 3, 2, 20.0],       # NaN order counts as an order, not in aov denominator
        ["US", 7.0, 1, 1, 7.0],         # refunded excluded; duplicate row 15 counted once
        ["unknown", 5.0, 1, 1, 5.0],
    ]


def test_share_small(load):
    m = load("ex04_groupby_transform")
    sh = m.user_share(*small())
    assert sh.values.tolist() == [["DE", 1, 40.0, 1.0], ["DE", 2, 0.0, 0.0],
                                  ["US", 4, 7.0, 1.0], ["unknown", 3, 5.0, 1.0]]


def test_real_data_three_ways(load):
    m = load("ex04_groupby_transform")
    users, orders = m.load()
    s = m.country_summary(users, orders)
    assert m.brute_force_summary(users, orders) == list(s.itertuples(index=False, name=None))
    sh = m.user_share(users, orders)
    assert np.allclose(sh.groupby("country")["share"].sum(), 1.0, atol=0.01)
    with closing(m.to_sqlite(users, orders)) as conn:
        assert m.sql_country_summary(conn).equals(s)
        assert m.sql_user_share(conn).equals(sh)
    assert s["revenue"].is_monotonic_decreasing
