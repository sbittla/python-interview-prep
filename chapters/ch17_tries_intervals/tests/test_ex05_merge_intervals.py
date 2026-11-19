import random

import pytest


@pytest.mark.parametrize("intervals, expected", [
    ([[1, 3], [8, 10], [2, 6], [15, 18]], [[1, 6], [8, 10], [15, 18]]),
    ([[1, 4], [4, 5]], [[1, 5]]),                 # touching endpoints merge (closed)
    ([[1, 10], [2, 3]], [[1, 10]]),               # nested: max of ends
    ([[5, 5], [5, 7]], [[5, 7]]),
    ([[2, 3], [1, 1]], [[1, 1], [2, 3]]),         # integer-adjacent but not touching
    ([], []),
    ([[3, 4]], [[3, 4]]),
])
def test_cases(load, intervals, expected):
    assert load("ex05_merge_intervals").solve(intervals) == expected


def test_no_touching_merge(load):
    m = load("ex05_merge_intervals")
    assert m.solve([[1, 4], [4, 5]], merge_touching=False) == [[1, 4], [4, 5]]
    assert m.solve([[1, 4], [3, 5]], merge_touching=False) == [[1, 5]]


def test_input_not_mutated(load):
    data = [[1, 3], [2, 4]]
    out = load("ex05_merge_intervals").solve(data)
    out[0][1] = 99
    assert data == [[1, 3], [2, 4]]


def test_random_against_brute(load):
    m = load("ex05_merge_intervals")
    rng = random.Random(1)
    for _ in range(300):
        ivs = []
        for _ in range(rng.randint(0, 8)):
            s = rng.randint(0, 12)
            ivs.append([s, s + rng.randint(0, 4)])     # small range => many touching cases
        for touching in (True, False):
            assert m.solve(ivs, touching) == m.brute_force(ivs, touching), (ivs, touching)
