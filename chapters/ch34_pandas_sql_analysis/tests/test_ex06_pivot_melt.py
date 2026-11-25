from contextlib import closing

import numpy as np
import pandas as pd


def small():
    users = pd.DataFrame({"user_id": [1, 2], "country": ["DE", None]})
    orders = pd.DataFrame({
        "order_id": [1, 2, 3, 4, 4],
        "user_id": [1, 1, 2, 1, 1],
        "order_date": pd.to_datetime(["2026-01-05", "2026-01-20", "2026-02-01", "2026-02-02", "2026-02-02"]),
        "amount": [10.0, 5.0, 7.0, 1.0, 1.0],
        "status": ["paid", "paid", "paid", "paid", "paid"],
    })
    return users, orders


def test_wide_small(load):
    m = load("ex06_pivot_melt")
    wide = m.monthly_wide(*small())
    assert list(wide.columns) == ["2026-01", "2026-02", "total"]
    assert list(wide.index) == ["DE", "unknown"]
    assert wide.values.tolist() == [[15.0, 1.0, 16.0], [0.0, 7.0, 7.0]]


def test_long_round_trip(load):
    m = load("ex06_pivot_melt")
    long = m.to_long(m.monthly_wide(*small()))
    assert long.values.tolist() == [["DE", "2026-01", 15.0], ["DE", "2026-02", 1.0],
                                    ["unknown", "2026-02", 7.0]]


def test_real_data(load):
    m = load("ex06_pivot_melt")
    users, orders = m.load()
    wide = m.monthly_wide(users, orders)
    months = [c for c in wide.columns if c != "total"]
    assert np.allclose(wide[months].sum(axis=1), wide["total"], atol=0.05)
    brute = m.brute_force_wide(users, orders)
    assert brute == {c: row[:-1] for c, row in zip(wide.index, wide.values.tolist())}
    with closing(m.to_sqlite(users, orders)) as conn:
        assert m.sql_monthly_long(conn).equals(m.to_long(wide))


def test_pivot_vs_pivot_table(load):
    m = load("ex06_pivot_melt")
    assert m.pivot_or_error(pd.DataFrame({"k": [1, 1], "c": ["a", "a"], "v": [1, 2]})) == "ValueError"
    assert m.pivot_or_error(pd.DataFrame({"k": [1, 2], "c": ["a", "a"], "v": [1, 2]})) == "ok"
