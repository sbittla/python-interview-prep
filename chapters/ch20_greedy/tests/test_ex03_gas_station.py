import random

import pytest


def test_examples(load):
    m = load("ex03_gas_station")
    assert m.start_station([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
    assert m.start_station([2, 3, 4], [3, 4, 3]) == -1


@pytest.mark.parametrize("gas, cost, expected", [
    ([5], [4], 0), ([4], [5], -1), ([0, 0, 0], [0, 0, 0], 0), ([3, 1, 1], [1, 2, 2], 0),
])
def test_edge_cases(load, gas, cost, expected):
    assert load("ex03_gas_station").start_station(gas, cost) == expected


def test_random_against_brute_force(load):
    m = load("ex03_gas_station")
    rng = random.Random(3)
    for _ in range(400):
        n = rng.randint(1, 8)
        gas = [rng.randint(0, 5) for _ in range(n)]
        cost = [rng.randint(0, 5) for _ in range(n)]
        assert m.start_station(gas, cost) == m.brute_force(gas, cost)
