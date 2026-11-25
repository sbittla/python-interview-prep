from contextlib import closing
import math

import pandas as pd


def small():
    users = pd.DataFrame({"user_id": [1, 2, 3, 4],
                          "signup_date": pd.to_datetime(["2026-01-30", "2026-01-02", "2026-02-10", "2026-02-11"])})
    orders = pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5, 6],
        "user_id": [1, 1, 1, 3, 9, 2],
        "order_date": pd.to_datetime(["2026-02-01", "2026-02-20", "2026-03-01", "2026-03-05",
                                      "2026-01-15", "2026-01-03"]),
        "status": ["paid", "paid", "paid", "paid", "paid", "refunded"],
    })
    return users, orders


def test_small_known_matrix(load):
    m = load("ex09_cohort_retention")
    r = m.retention(*small())
    assert list(r.index) == ["2026-01", "2026-02"]
    assert r["size"].tolist() == [2, 2]                     # users who never order still count
    assert r.loc["2026-01", [0, 1, 2]].tolist() == [0.0, 0.5, 0.5]   # two Feb orders -> one active user
    assert r.loc["2026-02", 0] == 0.0 and r.loc["2026-02", 1] == 0.5
    assert math.isnan(r.loc["2026-02", 2])                  # 2026-04 not observed yet


def test_real_data_three_ways(load):
    m = load("ex09_cohort_retention")
    users, orders = m.load()
    r = m.retention(users, orders)
    as_lists = {c: [None if pd.isna(v) else v for v in row[1:]] for c, row in zip(r.index, r.values.tolist())}
    assert as_lists == m.brute_force_retention(users, orders)
    assert r["size"].sum() == len(users)
    with closing(m.to_sqlite(users, orders)) as conn:
        long = m.sql_retention(conn)
    assert len(long) > 0
    for row in long.itertuples():
        assert r.loc[row.cohort, row.k] == round(row.active / row.size, 3)
    observed = r.drop(columns="size").notna().sum().sum()
    assert observed == 4 * 6 - (1 + 2 + 3)                  # upper-left triangle
