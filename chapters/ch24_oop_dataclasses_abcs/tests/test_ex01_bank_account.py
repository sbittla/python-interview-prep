import pytest


@pytest.fixture
def m(load):
    mod = load("ex01_bank_account")
    mod.Account.reset_numbers()
    return mod


def test_example(m):
    a = m.Account(" Ada ", 1000)
    a.deposit(500)
    assert repr(a) == "Account(number=1001, owner='Ada', balance=1500)"
    assert a.history == [("open", 1000), ("deposit", 500)]


def test_numbers_are_sequential_and_shared(m):
    accts = [m.Account(f"u{i}") for i in range(3)]
    assert [a.number for a in accts] == [1001, 1002, 1003]
    assert "_next_number" not in vars(accts[0])


def test_history_is_per_instance(m):
    a, b = m.Account("a"), m.Account("b")
    a.deposit(5)
    assert b.history == [("open", 0)]
    assert a.history is not b.history


def test_balance_is_read_only(m):
    a = m.Account("a", 10)
    with pytest.raises(AttributeError):
        a.balance = 99
    assert a.balance == 10


@pytest.mark.parametrize("action", [
    lambda A: A("   "),
    lambda A: A("x", -1),
    lambda A: A("x", 5).withdraw(6),
    lambda A: A("x", 5).withdraw(0),
    lambda A: A("x", 5).deposit(-3),
])
def test_invalid_operations(m, action):
    with pytest.raises(ValueError):
        action(m.Account)


def test_failed_withdraw_leaves_state(m):
    a = m.Account("a", 5)
    with pytest.raises(ValueError):
        a.withdraw(6)
    assert a.balance == 5 and a.history == [("open", 5)]


def test_owner_setter_validates(m):
    a = m.Account("a")
    a.owner = "  Bea "
    assert a.owner == "Bea"
    with pytest.raises(ValueError):
        a.owner = ""
    assert a.owner == "Bea"


def test_interest_shadowing(m):
    a, b = m.Account("a", 1000), m.Account("b", 1000)
    b.interest_rate = 0.1
    assert a.add_interest() == 20 and b.add_interest() == 100
    assert m.Account.interest_rate == 0.02
    c = m.Account("c", 10)
    assert c.add_interest() == 0 and c.history == [("open", 10)]   # rounds to 0: no deposit
