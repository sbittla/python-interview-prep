import random

import pytest


@pytest.mark.parametrize("buildings, expected", [
    ([(2, 9, 10), (3, 7, 15), (5, 12, 12), (15, 20, 10), (19, 24, 8)],
     [[2, 10], [3, 15], [7, 12], [12, 0], [15, 10], [20, 8], [24, 0]]),
    ([(0, 2, 3), (2, 5, 3)], [[0, 3], [5, 0]]),          # touching, equal height: no point at 2
    ([(0, 2, 3), (2, 5, 1)], [[0, 3], [2, 1], [5, 0]]),  # right edge exclusive
    ([(1, 5, 2), (1, 3, 4)], [[1, 4], [3, 2], [5, 0]]),  # same left edge
    ([(1, 3, 2), (1, 3, 2)], [[1, 2], [3, 0]]),          # duplicates
    ([], []),
])
def test_cases(load, buildings, expected):
    assert load("ex10_skyline").solve(buildings) == expected


def test_random_against_brute(load):
    m = load("ex10_skyline")
    rng = random.Random(10)
    for _ in range(300):
        bs = []
        for _ in range(rng.randint(0, 7)):
            left = rng.randint(0, 10)
            bs.append((left, left + rng.randint(1, 5), rng.randint(1, 4)))
        out = m.solve(bs)
        assert out == m.brute_force(bs), bs
        assert all(a[1] != b[1] for a, b in zip(out, out[1:]))
        assert not out or out[-1][1] == 0
