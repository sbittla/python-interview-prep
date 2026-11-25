import pytest


def test_averager(load):
    m = load("ex02_closures")
    for make in (m.make_averager, m.make_averager_list):
        avg = make()
        assert [avg(x) for x in (10, 20, 60, 10)] == [10.0, 15.0, 30.0, 25.0]


def test_averagers_are_independent(load):
    m = load("ex02_closures")
    a, b = m.make_averager(), m.make_averager()
    a(100)
    assert b(2) == 2.0 and a(0) == 50.0


def test_averager_keeps_no_list(load):
    m = load("ex02_closures")
    avg = m.make_averager()
    for x in range(50):
        avg(x)
    state = m.free_vars(avg)
    assert state == {"count": 50, "total": sum(range(50))}
    assert not any(isinstance(v, list) for v in state.values())


def test_account_shares_one_cell(load):
    m = load("ex02_closures")
    deposit, withdraw, balance_of = m.make_account(100)
    assert deposit(50) == 150 and withdraw(30) == 120 and balance_of() == 120
    with pytest.raises(ValueError, match="insufficient funds"):
        withdraw(121)
    assert balance_of() == 120 and withdraw(120) == 0
    assert m.free_vars(deposit) == m.free_vars(withdraw) == {"balance": 0}
    other = m.make_account(5)
    assert other[2]() == 5 and balance_of() == 0


def test_free_vars_without_closure(load):
    assert load("ex02_closures").free_vars(lambda x: x) == {}
