from contextlib import closing
import random
import sqlite3

import pandas as pd
import pytest
from pandas.errors import MergeError


def test_left_and_anti_small(load):
    m = load("ex05_merge_joins")
    users = pd.DataFrame({"user_id": [1, 2, 3]})
    orders = pd.DataFrame({"order_id": [10, 11, 12, 12, 13], "user_id": [1, 1, 9, 9, 3]})
    assert m.orders_per_user(users, orders).values.tolist() == [[1, 2], [2, 0], [3, 1]]
    assert m.orphan_orders(orders, users) == [12]
    assert m.orphan_orders(orders.iloc[0:0], users) == []


def test_real_data_vs_sql(load):
    m = load("ex05_merge_joins")
    users, orders = m.load()
    with closing(sqlite3.connect(":memory:")) as conn:
        users.to_sql("users", conn, index=False)
        orders.to_sql("orders", conn, index=False)
        assert m.sql_orders_per_user(conn).equals(m.orders_per_user(users, orders))
        assert m.sql_orphan_orders(conn) == m.orphan_orders(orders, users) == [1086]


def test_validate_raises_on_duplicate_keys(load):
    m = load("ex05_merge_joins")
    orders = pd.DataFrame({"order_id": [1, 2], "user_id": [5, 6]})
    ok = m.checked_lookup(orders, pd.DataFrame({"user_id": [5, 6], "tier": ["a", "b"]}))
    assert ok["tier"].tolist() == ["a", "b"]
    with pytest.raises(MergeError):
        m.checked_lookup(orders, pd.DataFrame({"user_id": [5, 5], "tier": ["a", "b"]}))


def test_join_row_count_random(load):
    m = load("ex05_merge_joins")
    rng = random.Random(5)
    for _ in range(200):
        a = [rng.randint(0, 4) for _ in range(rng.randint(0, 8))]
        b = [rng.randint(0, 4) for _ in range(rng.randint(0, 8))]
        expected = len(pd.DataFrame({"k": a}).merge(pd.DataFrame({"k": b}), on="k"))
        assert m.join_row_count(a, b) == m.brute_force_join_count(a, b) == expected
