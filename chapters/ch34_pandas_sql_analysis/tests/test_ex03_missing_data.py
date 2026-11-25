from contextlib import closing

import numpy as np
import pandas as pd


def test_clean_small(load):
    m = load("ex03_missing_data")
    df = pd.DataFrame({"order_id": [3, 1, 2, 2, 4], "user_id": [1, 1, 1, 1, 2],
                       "amount": [np.nan, 10.0, 30.0, 30.0, np.nan], "status": ["paid"] * 5})
    before = df.copy()
    out = m.clean_orders(df)
    assert out["order_id"].tolist() == [1, 2, 3, 4]                 # duplicate row removed
    assert out["amount"].tolist() == [10.0, 30.0, 20.0, 20.0]       # user median 20; user 2 -> global median 20
    assert out["imputed"].tolist() == [False, False, True, True]
    assert df.equals(before)


def test_global_fallback_differs_from_user_median(load):
    m = load("ex03_missing_data")
    df = pd.DataFrame({"order_id": [1, 2, 3, 4], "user_id": [1, 1, 2, 3],
                       "amount": [1.0, 3.0, 100.0, np.nan], "status": ["paid"] * 4})
    out = m.clean_orders(df)
    assert out.loc[out["order_id"] == 4, "amount"].item() == 3.0    # median of 1, 3, 100


def test_real_data(load):
    m = load("ex03_missing_data")
    users, orders = m.load()
    out = m.clean_orders(orders)
    assert out.equals(m.brute_force_clean(orders))
    assert out["amount"].notna().all() and len(out) == len(orders) - 1


def test_country_groups_and_sql(load):
    m = load("ex03_missing_data")
    users, orders = m.load()
    dropped = m.revenue_by_country(users, orders, keep_unknown=False)
    kept = m.revenue_by_country(users, orders, keep_unknown=True)
    assert "unknown" not in dropped.index and "unknown" in kept.index
    assert kept.drop("unknown").equals(dropped)
    with closing(m.to_sqlite(users, orders)) as conn:
        sql = m.sql_revenue_by_country(conn)
    assert list(sql.index) == list(kept.index)
    assert np.allclose(sql.to_numpy(), kept.to_numpy(), atol=0.011)


def test_null_semantics(load):
    m = load("ex03_missing_data")
    assert m.null_semantics() == {
        "pandas_sum_all_null": 0.0, "sql_sum_all_null": None,
        "pandas_count": 2, "sql_count": 2, "pandas_size": 3, "sql_count_star": 3,
        "pandas_mean": 2.0, "sql_avg": 2.0}
