import random

import pytest

NAME = "ex02_container_most_water"


def test_examples(load):
    m = load(NAME)
    assert m.solve([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert m.solve([1, 1]) == 1


@pytest.mark.parametrize("heights, expected", [
    ([], 0), ([5], 0), ([0, 0], 0), ([4, 3, 2, 1, 4], 16), ([1, 2, 1], 2), ([2, 9, 9, 1, 1, 1], 9),
])
def test_edge_cases(load, heights, expected):
    assert load(NAME).solve(heights) == expected


def test_random_against_brute(load):
    m = load(NAME)
    rng = random.Random(1002)
    for _ in range(400):
        h = [rng.randint(0, 10) for _ in range(rng.randint(0, 15))]
        assert m.solve(h) == m.brute_force(h)


def test_moving_taller_wall_is_wrong(load):
    m = load(NAME)
    h = [1, 8, 6, 2, 5, 4, 8, 3, 7]
    assert m.wrong_move_taller(h) < m.solve(h)
