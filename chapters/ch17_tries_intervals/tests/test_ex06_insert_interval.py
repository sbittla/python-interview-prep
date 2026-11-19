import random

import pytest


@pytest.mark.parametrize("intervals, new, expected", [
    ([[1, 3], [6, 9]], [2, 5], [[1, 5], [6, 9]]),
    ([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8], [[1, 2], [3, 10], [12, 16]]),
    ([[1, 2], [5, 6]], [2, 5], [[1, 6]]),         # touches both neighbours
    ([[1, 2], [5, 6]], [3, 4], [[1, 2], [3, 4], [5, 6]]),
    ([], [4, 7], [[4, 7]]),
    ([[1, 2]], [5, 6], [[1, 2], [5, 6]]),
    ([[5, 6]], [1, 2], [[1, 2], [5, 6]]),
    ([[3, 4]], [0, 9], [[0, 9]]),
])
def test_cases(load, intervals, new, expected):
    m = load("ex06_insert_interval")
    snapshot = [iv[:] for iv in intervals]
    assert m.solve(intervals, new) == expected
    assert intervals == snapshot


def test_random_against_brute(load):
    m = load("ex06_insert_interval")
    rng = random.Random(6)
    for _ in range(300):
        ivs, x = [], rng.randint(0, 2)
        for _ in range(rng.randint(0, 6)):
            s = x + rng.randint(0, 2)
            e = s + rng.randint(0, 3)
            ivs.append([s, e])
            x = e + 1 + rng.randint(0, 2)             # strictly disjoint, never touching
        a = rng.randint(0, 25)
        new = [a, a + rng.randint(0, 6)]
        assert m.solve(ivs, new) == m.brute_force(ivs, new), (ivs, new)
