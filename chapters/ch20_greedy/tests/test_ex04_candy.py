import random

import pytest


def test_examples(load):
    m = load("ex04_candy")
    assert m.min_candies([1, 0, 2]) == 5
    assert m.min_candies([1, 2, 2]) == 4


@pytest.mark.parametrize("ratings, expected", [
    ([5], 1), ([3, 3, 3], 3), ([5, 4, 3, 2, 1], 15), ([1, 2, 3, 2, 1], 9),
])
def test_edge_cases(load, ratings, expected):
    assert load("ex04_candy").min_candies(ratings) == expected


def test_distribution_respects_rules_and_matches_brute(load):
    m = load("ex04_candy")
    rng = random.Random(4)
    for _ in range(200):
        r = [rng.randint(0, 4) for _ in range(rng.randint(1, 10))]
        c = m.distribute(r)
        assert min(c) >= 1
        for i in range(len(r) - 1):
            if r[i] > r[i + 1]:
                assert c[i] > c[i + 1]
            if r[i + 1] > r[i]:
                assert c[i + 1] > c[i]
        assert sum(c) == m.brute_force(r)
