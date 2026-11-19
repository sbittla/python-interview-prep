import random

import pytest


def test_examples(load):
    m = load("ex06_daily_temperatures")
    assert m.days_until_warmer([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]


@pytest.mark.parametrize("temps, expected", [
    ([], []), ([50], [0]), ([50, 50], [0, 0]), ([30, 40, 50], [1, 1, 0]),
    ([50, 40, 30], [0, 0, 0]), ([50, 50, 51], [2, 1, 0]),
])
def test_edge_cases(load, temps, expected):
    m = load("ex06_daily_temperatures")
    assert m.days_until_warmer(temps) == expected
    assert m.jump_back(temps) == expected


def test_random_against_brute(load):
    m = load("ex06_daily_temperatures")
    rng = random.Random(13)
    for _ in range(400):
        temps = [rng.randint(30, 36) for _ in range(rng.randint(0, 15))]
        assert m.days_until_warmer(temps) == m.brute_force(temps) == m.jump_back(temps)
