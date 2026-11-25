import dataclasses

import pytest


@pytest.fixture
def m(load):
    return load("ex07_dataclass_inventory")


def test_version_order_and_parse(m):
    V = m.Version
    vs = [V.parse(s) for s in ["1.10", "1.9.3", "2", "1.9", "0.0.1"]]
    assert [str(v) for v in sorted(vs)] == ["0.0.1", "1.9.0", "1.9.3", "1.10.0", "2.0.0"]
    assert V.parse("1.10") > V.parse("1.9") and V(1) == V.parse("1.0.0")
    assert len({V(1), V(1, 0, 0), V(1, 0, 1)}) == 2


@pytest.mark.parametrize("text", ["", "1.2.3.4", "1..2", "a.b", "-1", "1.²"])
def test_version_bad(m, text):
    with pytest.raises(ValueError):
        m.Version.parse(text)


def test_frozen_and_slots(m):
    it = m.Item("bolt", 5, 10)
    with pytest.raises(dataclasses.FrozenInstanceError):
        it.qty = 0
    assert not hasattr(it, "__dict__") and not hasattr(m.Location("A", 1), "__dict__")
    assert hash(it) == hash(m.Item("bolt", 5, 10))


@pytest.mark.parametrize("args", [("", 1), ("x", -1), ("x", 1, -1)])
def test_item_validation(m, args):
    with pytest.raises(ValueError):
        m.Item(*args)


def test_restock_returns_new(m):
    it = m.Item("bolt", 5, 10)
    new = m.restock(it, 5)
    assert new.qty == 15 and it.qty == 10 and new is not it
    with pytest.raises(ValueError):
        m.restock(it, -11)                    # __post_init__ re-runs on replace


def test_cart_default_factory(m):
    c1, c2 = m.Cart("a"), m.Cart("b")
    c1.add(m.Item("x", 10, 3))
    assert c2.items == [] and c1.total == 30
    assert m.Cart.__hash__ is None
    assert m.Cart("a") == m.Cart("a")


def test_by_location_and_report(m):
    a1, b3 = m.Location("A", 1), m.Location("B", 3)
    items = [m.Item("nut", 3, 100, a1), m.Item("bolt", 5, 100, a1),
             m.Item("drill", 4999, 2, b3), m.Item("glue", 250, 4), m.Item("tape", 500, 2)]
    assert m.by_location(items) == {a1: ["bolt", "nut"], b3: ["drill"]}
    rows = m.report(items)
    assert [r["name"] for r in rows] == ["drill", "glue", "tape", "bolt", "nut"]
    assert rows[0]["location"] == {"aisle": "B", "shelf": 3}
    assert m.by_location([]) == {} and m.report([]) == []


def test_documentation_mutable_default_rejected():
    """Documentation test: checks the language rule from the hints, so it passes on stubs."""
    with pytest.raises(ValueError):
        @dataclasses.dataclass
        class Bad:
            tags: list = []


def test_hand_written_rung(m):
    assert m.HandItem("a", 1) == m.HandItem("a", 1) and repr(m.HandItem("a", 1)) == \
        "HandItem(name='a', price_cents=1, qty=0)"
