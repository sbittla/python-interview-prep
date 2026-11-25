import csv
import io
import json
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.mark.parametrize("price, cents", [("19.99", 1999), ("5.5", 550), ("12", 1200),
                                          ("0.10", 10), ("0.29", 29), ("1.15", 115)])
def test_to_cents_exact(load, price, cents):
    # int(float("0.29") * 100) == 28 and int(float("1.15") * 100) == 114: floats fail here
    assert load("ex04_csv_json_transform").to_cents(price) == cents


def test_orders_file(load):
    m = load("ex04_csv_json_transform")
    with open(DATA / "orders.csv", encoding="utf-8", newline="") as f:
        c = m.orders_to_customers(csv.DictReader(f))
    assert list(c) == ["Asha", "Bo", "Chen", "Dana"]
    assert c["Asha"] == {"country": "IN", "orders": 2, "total_cents": 4028,
                         "items": ["Gizmo", "Widget, large"]}
    assert c["Bo"]["items"] == ['Cable "USB-C"', "Gadget"] and c["Bo"]["total_cents"] == 1450
    assert c["Dana"]["country"] is None
    assert json.loads(json.dumps(c)) == c


def test_inline_csv_quoting(load):
    m = load("ex04_csv_json_transform")
    text = 'order_id,customer,country,item,qty,unit_price\n1,"Lee, Jr",UK,"a ""b""",3,0.10\n'
    c = m.orders_to_customers(csv.DictReader(io.StringIO(text, newline="")))
    assert c == {"Lee, Jr": {"country": "UK", "orders": 1, "total_cents": 30, "items": ['a "b"']}}
    assert m.orders_to_customers([]) == {}


def test_flatten(load):
    m = load("ex04_csv_json_transform")
    assert m.flatten({"a": {"b": 1}, "c": [5, {"d": None}]}) == {"a.b": 1, "c.0": 5, "c.1.d": None}
    assert m.flatten({}) == {} and m.flatten({"a": [], "b": {}}) == {}
    assert m.flatten({"x": [[1, 2], [3]]}) == {"x.0.0": 1, "x.0.1": 2, "x.1.0": 3}
    assert m.flatten({"k": False}) == {"k": False}


def test_to_csv_union_header(load):
    m = load("ex04_csv_json_transform")
    out = m.to_csv([{"b": 1, "a": "x,y"}, {"c": 3}])
    assert out == 'a,b,c\n"x,y",1,\n,,3\n'
    rows = list(csv.DictReader(io.StringIO(out)))
    assert rows[0]["a"] == "x,y" and rows[1]["c"] == "3"
