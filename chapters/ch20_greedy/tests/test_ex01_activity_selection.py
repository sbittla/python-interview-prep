import random

import pytest


def test_examples(load):
    m = load("ex01_activity_selection")
    assert m.max_activities([(1, 4), (3, 5), (0, 6), (5, 7), (8, 9), (5, 9)]) == 3
    assert m.min_removals([(1, 2), (2, 3), (3, 4), (1, 3)]) == 1


@pytest.mark.parametrize("intervals, expected", [
    ([], 0), ([(1, 2)], 1), ([(1, 2), (2, 3), (3, 4)], 3), ([(1, 5)] * 4, 1), ([(0, 10), (1, 2), (3, 4)], 2),
])
def test_edge_cases(load, intervals, expected):
    assert load("ex01_activity_selection").max_activities(intervals) == expected


def test_select_is_compatible(load):
    m = load("ex01_activity_selection")
    chosen = m.select([(1, 4), (3, 5), (0, 6), (5, 7), (8, 9), (5, 9)])
    assert all(a[1] <= b[0] for a, b in zip(chosen, chosen[1:]))


def test_random_against_brute_force(load):
    m = load("ex01_activity_selection")
    rng = random.Random(20)
    for _ in range(150):
        ivs = []
        for _ in range(rng.randint(0, 8)):
            s = rng.randint(0, 15)
            ivs.append((s, s + rng.randint(1, 6)))
        assert m.max_activities(ivs) == m.brute_force(ivs)
