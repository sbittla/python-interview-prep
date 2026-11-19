import random

import pytest

NAME = "ex12_range_update_difference"


def test_examples(load):
    m = load(NAME)
    assert m.solve(5, [(1, 3, 2), (2, 4, 3), (0, 2, -2)]) == [-2, 0, 3, 5, 3]
    assert m.peak_load([(2, 1, 5), (3, 3, 7)]) == 5


@pytest.mark.parametrize("n, updates, expected", [
    (1, [], [0]), (3, [(0, 2, 1)], [1, 1, 1]), (4, [(3, 3, 4)], [0, 0, 0, 4]),
    (3, [(0, 0, 5), (0, 0, -5)], [0, 0, 0]),
])
def test_edge_cases(load, n, updates, expected):
    assert load(NAME).solve(n, updates) == expected


def test_peak_load_edges(load):
    m = load(NAME)
    assert m.peak_load([]) == 0
    assert m.peak_load([(2, 1, 5), (3, 5, 7)]) == 3          # drop-off, then pick-up at 5
    assert m.peak_load([(4, 0, 1)]) == 4


def test_random_against_brute(load):
    m = load(NAME)
    rng = random.Random(1012)
    for _ in range(300):
        n = rng.randint(1, 12)
        updates = []
        for _ in range(rng.randint(0, 8)):
            lo, hi = sorted(rng.randint(0, n - 1) for _ in range(2))
            updates.append((lo, hi, rng.randint(-5, 5)))
        assert m.solve(n, updates) == m.brute_force(n, updates)
        trips = []
        for _ in range(rng.randint(0, 6)):
            s = rng.randint(0, 9)
            trips.append((rng.randint(1, 5), s, rng.randint(s + 1, 10)))
        assert m.peak_load(trips) == m.peak_load_brute(trips)


def test_inclusive_end_overcounts(load):
    assert load(NAME).wrong_inclusive_end([(2, 1, 5), (3, 5, 7)]) == 5
