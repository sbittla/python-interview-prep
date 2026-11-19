import random

import pytest


def test_examples(load):
    m = load("ex07_largest_rectangle")
    assert m.largest_rectangle([2, 1, 5, 6, 2, 3]) == 10
    assert m.largest_rectangle([2, 4]) == 4


@pytest.mark.parametrize("heights, expected", [
    ([], 0), ([0], 0), ([7], 7), ([3, 3, 3], 9), ([1, 2, 3, 4, 5], 9), ([5, 4, 3, 2, 1], 9),
    ([2, 0, 2], 2), ([6, 2, 5, 4, 5, 1, 6], 12),
])
def test_edge_cases(load, heights, expected):
    m = load("ex07_largest_rectangle")
    assert m.largest_rectangle(heights) == expected
    assert m.with_boundaries(heights) == expected


def test_does_not_mutate_input(load):
    h = [2, 1, 2]
    load("ex07_largest_rectangle").largest_rectangle(h)
    assert h == [2, 1, 2]


def test_random_against_brute(load):
    m = load("ex07_largest_rectangle")
    rng = random.Random(17)
    for _ in range(400):
        h = [rng.randint(0, 6) for _ in range(rng.randint(0, 12))]
        assert m.largest_rectangle(h) == m.with_boundaries(h) == m.brute_force(h)
