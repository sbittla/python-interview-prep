import random

import pytest

M = "ex09_stock_cooldown"


def test_examples(load):
    m = load(M)
    assert m.max_profit([1, 2, 3, 0, 2]) == 3
    assert (m.max_profit([5, 4, 3]), m.max_profit([])) == (0, 0)


@pytest.mark.parametrize("prices, expected", [
    ([], 0), ([3], 0), ([1, 4], 3), ([4, 1], 0), ([1, 2, 1, 2], 1), ([1, 2, 1, 1, 2], 2),
    ([2, 1, 4, 5, 2, 9, 7], 10), ([3, 3, 3], 0),
])
def test_edges(load, prices, expected):
    m = load(M)
    assert m.max_profit(prices) == m.max_profit_table(prices) == m.max_profit_memo(prices) == expected
    assert m.max_profit_brute(prices) == expected


def test_returns_int(load):
    assert isinstance(load(M).max_profit([5, 4, 3]), int)


def test_random_against_brute(load):
    m = load(M)
    rng = random.Random(31)
    for _ in range(300):
        prices = [rng.randint(0, 9) for _ in range(rng.randint(0, 12))]
        assert m.max_profit(prices) == m.max_profit_table(prices) == m.max_profit_brute(prices)


def test_long_input(load):
    m = load(M)
    prices = [(0, 2, 1)[i % 3] for i in range(100_000)]   # buy 0, sell 2, cool down on 1
    assert m.max_profit(prices) == m.max_profit_table(prices) == 2 * (100_000 // 3)
