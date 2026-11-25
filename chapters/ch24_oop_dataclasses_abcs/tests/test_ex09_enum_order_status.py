import pytest


@pytest.fixture
def m(load):
    return load("ex09_enum_order_status")


def test_happy_path(m):
    o = m.Order("A1")
    o.advance("paid")
    o.advance(m.Status.SHIPPED)
    o.advance("delivered")
    assert [s.value for s in o.trail] == ["pending", "paid", "shipped", "delivered"]
    assert o.status is m.Status.DELIVERED


@pytest.mark.parametrize("path", [["cancelled"], ["paid", "cancelled"]])
def test_cancel_paths(m, path):
    o = m.Order("x")
    for step in path:
        o.advance(step)
    assert o.status is m.Status.CANCELLED


@pytest.mark.parametrize("path", [["shipped"], ["paid", "paid"], ["cancelled", "paid"],
                                  ["paid", "shipped", "cancelled"], ["pending"]])
def test_illegal_transitions(m, path):
    o = m.Order("x")
    with pytest.raises(m.InvalidTransition):
        for step in path:
            o.advance(step)
    assert issubclass(m.InvalidTransition, ValueError)


def test_failed_advance_keeps_state(m):
    o = m.Order("x")
    with pytest.raises(ValueError):
        o.advance("refunded")
    with pytest.raises(m.InvalidTransition):
        o.advance("delivered")
    assert o.status is m.Status.PENDING and o.trail == [m.Status.PENDING]


def test_terminal_states(m):
    assert m.TRANSITIONS[m.Status.DELIVERED] == frozenset()
    assert set(m.TRANSITIONS) == set(m.Status)


def test_lookup(m):
    assert m.Status("paid") is m.Status.PAID and m.Status["PAID"] is m.Status.PAID
    with pytest.raises(KeyError):
        m.Status["paid"]
    assert m.Status.PAID != "paid"


def test_sort_orders(m):
    P = m.Priority
    orders = [m.Order("b", P.LOW), m.Order("c", P.HIGH), m.Order("a", P.HIGH), m.Order("d")]
    assert m.sort_orders(orders) == ["a", "c", "d", "b"]
    assert m.sort_orders([]) == []
    assert P.HIGH == 3 and P.LOW < P.NORMAL


def test_flags(m):
    R, W, D = m.Perm.READ, m.Perm.WRITE, m.Perm.DELETE
    assert (R.value, W.value, D.value) == (1, 2, 4)
    assert m.can(R | W, R) and m.can(R | W, R | W) and not m.can(R, R | D)
    assert m.can(R | W | D, D | W) and not m.can(W, R)


def test_naive_rung_accepts_typo(m):
    assert m.naive_advance("pending", "payed") == "payed"
