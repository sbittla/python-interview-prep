import pytest


def test_examples(load):
    m = load("ex08_greedy_vs_dp")
    assert (m.greedy_coins([1, 3, 4], 6), m.min_coins([1, 3, 4], 6)) == (3, 2)
    assert m.find_counterexample([1, 5, 10, 25], 200) is None


@pytest.mark.parametrize("coins, expected", [
    ([1, 3, 4], 6), ([1, 7, 10], 14), ([1, 15, 25], 30), ([1, 2, 5, 10], None),
])
def test_counterexamples(load, coins, expected):
    assert load("ex08_greedy_vs_dp").find_counterexample(coins, 100) == expected


@pytest.mark.parametrize("coins, amount, expected", [
    ([2], 3, -1), ([1], 0, 0), ([3, 5], 9, 3), ([3, 5], 7, -1), ([186, 419, 83, 408], 6249, 20),
])
def test_min_coins(load, coins, amount, expected):
    assert load("ex08_greedy_vs_dp").min_coins(coins, amount) == expected


def test_knapsack(load):
    m = load("ex08_greedy_vs_dp")
    items = [(60, 10), (100, 20), (120, 30)]
    assert m.fractional_knapsack(items, 50) == pytest.approx(240.0)
    assert m.greedy_01_by_ratio(items, 50) == 160
    assert m.knapsack_01(items, 50) == 220
    assert m.knapsack_01([], 10) == 0
