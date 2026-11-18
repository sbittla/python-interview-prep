import random

import pytest


def test_examples(load):
    m = load("ex10_min_arrows")
    assert m.min_arrows([[10, 16], [2, 8], [1, 6], [7, 12]]) == 2
    assert m.min_rooms([(0, 30), (5, 10), (15, 20)]) == 2
    assert m.min_boats([3, 2, 2, 1], 3) == 3


@pytest.mark.parametrize("balloons, expected", [
    ([], 0), ([[1, 2], [2, 3]], 1), ([[1, 2], [3, 4]], 2), ([[1, 10], [2, 3], [4, 5]], 2),
])
def test_arrows_edge(load, balloons, expected):
    assert load("ex10_min_arrows").min_arrows(balloons) == expected


def test_rooms_random_against_brute(load):
    m = load("ex10_min_arrows")
    rng = random.Random(10)
    for _ in range(200):
        ms = []
        for _ in range(rng.randint(0, 8)):
            s = rng.randint(0, 20)
            ms.append((s, s + rng.randint(1, 6)))
        assert m.min_rooms(ms) == m.min_rooms_brute(ms)


@pytest.mark.parametrize("weights, limit, expected", [
    ([1, 2], 3, 1), ([3, 5, 3, 4], 5, 4), ([5, 1, 4, 2], 6, 2), ([], 3, 0),
])
def test_boats(load, weights, limit, expected):
    assert load("ex10_min_arrows").min_boats(weights, limit) == expected
