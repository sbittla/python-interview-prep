import itertools

import pytest


def test_examples(load):
    m = load("ex03_print_in_order")
    assert m.run_in_order([2, 0, 1]) == ["first", "second", "third"]
    assert m.ping_pong(2) == ["ping", "pong", "ping", "pong"]
    assert m.zero_even_odd(3) == "010203"


@pytest.mark.parametrize("order", list(itertools.permutations(range(3))))
def test_every_start_order(load, order):
    m = load("ex03_print_in_order")
    for _ in range(20):
        assert m.run_in_order(list(order)) == ["first", "second", "third"]


@pytest.mark.parametrize("n", [0, 1, 7, 500])
def test_ping_pong(load, n):
    assert load("ex03_print_in_order").ping_pong(n) == ["ping", "pong"] * n


@pytest.mark.parametrize("n, expected", [(0, ""), (1, "01"), (2, "0102"), (5, "0102030405"),
                                         (12, "".join(f"0{i}" for i in range(1, 13)))])
def test_zero_even_odd(load, n, expected):
    assert load("ex03_print_in_order").zero_even_odd(n) == expected
