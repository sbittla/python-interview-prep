import pandas as pd
import pytest


def test_types_and_profile(load):
    m = load("ex01_load_inspect")
    df = m.load_orders()
    assert pd.api.types.is_datetime64_any_dtype(df["order_date"])
    assert df["amount"].dtype == "float64" and df["order_id"].dtype == "int64"
    p = m.profile(df)
    assert p == m.brute_force_profile()
    assert p["rows"] == 87 and p["nulls"] == {"amount": 3}
    assert p["first"] == "2026-01-23" and p["last"] == "2026-06-29"


def test_profile_small_file(load, tmp_path):
    m = load("ex01_load_inspect")
    f = tmp_path / "o.csv"
    f.write_text("order_id,user_id,order_date,amount,status\n"
                 "1,7,2026-02-01,,paid\n2,7,2026-01-05,3.5,paid\n3,8,2026-03-09,1.0,\n")
    p = m.profile(m.load_orders(f))
    assert p == {"rows": 3, "columns": ["order_id", "user_id", "order_date", "amount", "status"],
                 "nulls": {"amount": 1, "status": 1}, "users": 2,
                 "first": "2026-01-05", "last": "2026-03-09"}
    assert p == m.brute_force_profile(f)


def test_empty_file(load, tmp_path):
    m = load("ex01_load_inspect")
    f = tmp_path / "e.csv"
    f.write_text("order_id,user_id,order_date,amount,status\n")
    assert m.profile(m.load_orders(f))["first"] is None
    assert m.brute_force_profile(f)["rows"] == 0


@pytest.mark.parametrize("a, b, expected", [
    ({"x": 1, "y": 2}, {"y": 10, "z": 5}, {"x": 1.0, "y": 12.0, "z": 5.0}),
    ({}, {"q": 1}, {"q": 1.0}),
    ({"b": 1, "a": 2}, {}, {"a": 2.0, "b": 1.0}),
])
def test_add_aligned(load, a, b, expected):
    m = load("ex01_load_inspect")
    out = m.add_aligned(pd.Series(a, dtype="float64"), pd.Series(b, dtype="float64"))
    assert out.to_dict() == expected
    assert list(out.index) == sorted(expected)
