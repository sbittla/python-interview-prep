import random

import pytest


def test_examples(load):
    m = load("ex05_stock_span")
    assert m.spans([100, 80, 60, 70, 60, 75, 85]) == [1, 1, 1, 2, 1, 4, 6]


@pytest.mark.parametrize("prices, expected", [
    ([], []), ([7], [1]), ([5, 5, 5], [1, 2, 3]), ([1, 2, 3], [1, 2, 3]), ([3, 2, 1], [1, 1, 1]),
    ([2, 1, 2], [1, 1, 3]),
])
def test_edge_cases(load, prices, expected):
    assert load("ex05_stock_span").spans(prices) == expected


def test_online_interface(load):
    s = load("ex05_stock_span").StockSpanner()
    assert [s.next(p) for p in (31, 41, 48, 59, 79)] == [1, 2, 3, 4, 5]


def test_random_against_brute(load):
    m = load("ex05_stock_span")
    rng = random.Random(11)
    for _ in range(400):
        prices = [rng.randint(1, 6) for _ in range(rng.randint(0, 15))]
        assert m.spans(prices) == m.brute_force(prices)
