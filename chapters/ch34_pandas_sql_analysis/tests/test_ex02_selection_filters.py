from contextlib import closing

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def small():
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5, 6],
        "user_id": [10, 11, 10, 12, 13, 11],
        "order_date": pd.to_datetime(["2026-01-01", "2026-01-31", "2026-02-01",
                                      "2026-01-15", "2026-01-20", "2026-01-10"]),
        "amount": [50.0, 80.0, 99.0, np.nan, 80.0, 20.0],
        "status": ["paid", "paid", "paid", "paid", "refunded", "paid"],
    })


def test_small_known_answer(load, small):
    m = load("ex02_selection_filters")
    out = m.big_paid_orders(small, 50, "2026-01-01", "2026-01-31")
    assert out["order_id"].tolist() == [2, 1]       # inclusive both ends; NaN and refunded excluded
    assert list(out.columns) == ["order_id", "user_id", "amount"]
    assert list(out.index) == [0, 1]


def test_matches_sql_and_brute(load):
    m = load("ex02_selection_filters")
    orders = m.load_orders()
    with closing(m.to_sqlite(orders)) as conn:
        for lo, start, end in [(0, "2026-01-01", "2026-12-31"), (60, "2026-02-01", "2026-04-30"),
                               (100, "2026-01-01", "2026-03-31"), (500, "2026-01-01", "2026-12-31")]:
            got = m.big_paid_orders(orders, lo, start, end)
            sql = m.sql_big_paid_orders(conn, lo, start, end)
            assert list(sql.columns) == list(got.columns)
            assert sql.values.tolist() == got.values.tolist()     # empty SQL results lose dtypes
            assert got["order_id"].tolist() == m.brute_force_big_paid(orders, lo, start, end)
            assert lo == 500 or len(got) > 0
    assert m.big_paid_orders(orders, 115, "2026-01-01", "2026-03-31")["order_id"].tolist() == [1015, 1008]


def test_label_vs_position(load, small):
    m = load("ex02_selection_filters")
    by_loc, by_iloc = m.label_vs_position(small)
    assert (by_loc, by_iloc) == (1, 3)


def test_flag_does_not_mutate(load, small):
    m = load("ex02_selection_filters")
    before = small.copy()
    out = m.flag_refund_risk(small, [11, 13])
    assert out["risk"].tolist() == [False, True, False, False, False, True]   # 5 is refunded
    assert small.equals(before)
