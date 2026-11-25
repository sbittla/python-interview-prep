import random

import pytest


@pytest.fixture
def m(load):
    return load("ex02_money_value_type")


def test_repr_str(m):
    assert repr(m.Money(1234, "USD")) == "Money(1234, 'USD')"
    assert str(m.Money(1234, "USD")) == "USD 12.34"
    assert str(m.Money(-5, "EUR")) == "EUR -0.05"
    assert str(m.Money(-100, "EUR")) == "EUR -1.00"
    assert str(m.Money(7, "JPY")) == "JPY 0.07"


def test_eq_hash_contract(m):
    M = m.Money
    assert M(5, "EUR") == M(5, "EUR") and hash(M(5, "EUR")) == hash(M(5, "EUR"))
    assert M(5, "EUR") != M(5, "USD")
    assert len({M(5, "EUR"), M(5, "EUR"), M(5, "USD")}) == 2
    assert (M(5, "USD") == 5) is False and (M(5, "USD") != "x") is True
    assert {M(1, "USD"): "a"}[M(1, "USD")] == "a"


def test_ordering(m):
    M = m.Money
    assert M(1, "USD") < M(2, "USD") <= M(2, "USD") and M(3, "USD") > M(2, "USD")
    assert sorted([M(3, "USD"), M(-1, "USD"), M(2, "USD")]) == [
        M(-1, "USD"), M(2, "USD"), M(3, "USD")]
    with pytest.raises(TypeError):
        M(1, "USD") < M(2, "EUR")
    with pytest.raises(TypeError):
        M(1, "USD") < 5


def test_arithmetic(m):
    M = m.Money
    assert M(150, "USD") + M(50, "USD") == M(200, "USD")
    assert M(150, "USD") - M(200, "USD") == M(-50, "USD")
    assert -M(3, "USD") == M(-3, "USD")
    assert M(3, "USD") * 4 == 4 * M(3, "USD") == M(12, "USD")
    assert sum([M(1, "USD"), M(2, "USD")]) == M(3, "USD")
    assert sum([], M(0, "USD")) == M(0, "USD")
    for bad in (lambda: M(1, "USD") + M(1, "EUR"), lambda: M(1, "USD") + 1,
                lambda: M(1, "USD") * 1.5, lambda: M(1, "USD") * M(1, "USD")):
        with pytest.raises(TypeError):
            bad()


def test_bool_and_validation(m):
    assert not m.Money(0, "USD") and m.Money(-1, "USD")
    for args in [(1.5, "USD"), (1, "usd"), (1, "US"), (1, "U$D"), (True, "USD")]:
        with pytest.raises(ValueError):
            m.Money(*args)


def test_allocate_examples(m):
    M = m.Money
    assert M(1000, "USD").allocate([1, 1, 1]) == [M(334, "USD"), M(333, "USD"), M(333, "USD")]
    assert M(5, "USD").allocate([3, 7]) == [M(2, "USD"), M(3, "USD")]
    assert M(5, "USD").allocate([0, 1, 1]) == [M(0, "USD"), M(3, "USD"), M(2, "USD")]
    assert M(0, "USD").allocate([1, 2]) == [M(0, "USD"), M(0, "USD")]
    with pytest.raises(ValueError):
        M(5, "USD").allocate([0, 0])


def test_allocate_random_conserves_cents(m):
    rng = random.Random(24)
    for _ in range(300):
        cents = rng.randint(-10_000, 10_000)
        ratios = [rng.randint(0, 5) for _ in range(rng.randint(1, 6))]
        if sum(ratios) == 0:
            ratios[0] = 1
        parts = m.Money(cents, "GBP").allocate(ratios)
        assert sum(p.cents for p in parts) == cents
        for p, r in zip(parts, ratios):
            assert abs(p.cents - cents * r / sum(ratios)) < 1 + 1e-9
            if r == 0:
                assert p.cents == 0


def test_eq_only_rung_is_unhashable(m):
    with pytest.raises(TypeError):
        hash(m.EqOnlyMoney(1, "USD"))


def test_foreign_types_get_notimplemented(m):
    M = m.Money

    class Probe:                           # only reachable if Money.__eq__ defers
        def __eq__(self, other):
            return isinstance(other, M)

        def __radd__(self, other):
            return "probe-radd"

        def __gt__(self, other):           # reflected form of Money < Probe
            return "probe-gt"

    assert M(1, "USD") == Probe()
    assert M(1, "USD") + Probe() == "probe-radd"
    assert (M(1, "USD") < Probe()) == "probe-gt"
    one = M(1, "USD")
    assert one.__eq__(5) is NotImplemented
    assert one.__add__(5) is NotImplemented
    assert one.__lt__(5) is NotImplemented
