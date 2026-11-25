import math

import pytest


@pytest.fixture
def m(load):
    mod = load("ex10_design_patterns")
    mod.Config.reset()
    return mod


def test_singleton(m):
    a = m.Config()
    a.settings["debug"] = True
    b = m.Config()
    assert a is b and b.settings == {"debug": True}
    m.Config.reset()
    assert m.Config() is not a and m.Config().settings == {"debug": False}


def test_factory(m):
    c = m.make_shape({"kind": "circle", "r": 2})
    assert isinstance(c, m.Circle) and math.isclose(c.area(), 4 * math.pi)
    assert m.make_shape({"kind": "rect", "w": 2, "h": 5}).area() == 10
    assert m.make_shape({"kind": "square", "side": 3}).area() == 9
    spec = {"kind": "square", "side": 1}
    m.make_shape(spec)
    assert spec == {"kind": "square", "side": 1}            # input not mutated
    with pytest.raises(ValueError, match=r"\['circle', 'rect', 'square'\]"):
        m.make_shape({"kind": "hexagon"})


def test_factory_open_for_extension(m):
    @m.register("tri")
    class Tri:
        def __init__(self, b, h):
            self.b, self.h = b, h

        def area(self):
            return self.b * self.h / 2

    assert m.make_shape({"kind": "tri", "b": 4, "h": 3}).area() == 6
    with pytest.raises(ValueError):
        m.make_shape_if_chain({"kind": "tri", "b": 4, "h": 3})


@pytest.mark.parametrize("pricing, prices, expected", [
    ("none", [1000, 500], 1500),
    ("pct10", [1000, 500], 1350),
    ("pct10", [5], 5),              # 4.5 rounds half up
    ("pct10", [], 0),
    ("b2g1", [1000, 500, 300, 200], 1800),
    ("b2g1", [100, 200], 300),
    ("b2g1", [3, 1, 2, 9, 9, 9], 30),
    ("b1g1", [5, 1, 4, 2], 9),
])
def test_strategies(m, pricing, prices, expected):
    strategies = {"none": m.no_discount, "pct10": m.percent_off(10),
                  "b2g1": m.buy_n_get_one(2), "b1g1": m.buy_n_get_one(1)}
    assert m.Checkout(strategies[pricing]).total(prices) == expected


def test_strategy_swap(m):
    co = m.Checkout()
    assert co.total([100]) == 100
    co.pricing = m.percent_off(50)
    assert co.total([100]) == 50


def test_observer(m):
    bus, seen = m.EventBus(), []
    u1 = bus.subscribe("e", lambda p: seen.append(("one", p)))
    bus.subscribe("e", lambda p: seen.append(("two", p)))
    bus.subscribe("other", lambda p: seen.append(("other", p)))
    assert bus.publish("e", 1) == 2 and seen == [("one", 1), ("two", 1)]
    u1()
    assert bus.publish("e", 2) == 1 and seen[-1] == ("two", 2)
    assert bus.publish("nobody", 0) == 0


def test_handler_may_unsubscribe_during_publish(m):
    bus, seen = m.EventBus(), []
    unsub = []

    def once(p):
        seen.append(p)
        unsub[0]()

    unsub.append(bus.subscribe("e", once))
    bus.subscribe("e", lambda p: seen.append(p * 10))
    assert bus.publish("e", 1) == 2 and bus.publish("e", 2) == 1
    assert seen == [1, 10, 20]
