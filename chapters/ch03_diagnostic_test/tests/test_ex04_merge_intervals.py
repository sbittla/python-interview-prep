import random

import pytest


def test_examples(load):
    m = load("ex04_merge_intervals")
    assert m.merge([[8, 10], [1, 3], [2, 6]]) == [[1, 6], [8, 10]]
    assert m.merge([[1, 3], [3, 5]]) == [[1, 5]]


@pytest.mark.parametrize("intervals, expected", [
    ([], []), ([[4, 4]], [[4, 4]]), ([[1, 10], [2, 3]], [[1, 10]]),
    ([[5, 6], [1, 5]], [[1, 6]]), ([[1, 2], [4, 5]], [[1, 2], [4, 5]]),
    ([[2, 3], [2, 3], [2, 3]], [[2, 3]]), ([[-3, -1], [-1, 0]], [[-3, 0]]),
])
def test_edge_cases(load, intervals, expected):
    m = load("ex04_merge_intervals")
    assert m.merge(intervals) == expected
    assert m.brute_force(intervals) == expected


def test_matches_brute_force_on_random_inputs(load):
    m = load("ex04_merge_intervals")
    rng = random.Random(3)
    for _ in range(200):
        ivs = []
        for _ in range(rng.randint(0, 8)):
            a = rng.randint(-10, 10)
            ivs.append([a, a + rng.randint(0, 5)])
        assert m.merge(ivs) == m.brute_force(ivs)


def test_input_not_mutated(load):
    m = load("ex04_merge_intervals")
    ivs = [[2, 6], [1, 3]]
    out = m.merge(ivs)
    out[0][1] = 99
    assert ivs == [[2, 6], [1, 3]]


def test_scoring(load):
    m = load("ex04_merge_intervals")
    assert m.score_submission(m.merge) == 4
    assert m.score_submission(m.tempting_no_max) == 3
    assert m.score_submission(lambda ivs: None) == 0
    assert m.CASES[0][0] == [[8, 10], [1, 3], [2, 6]]   # scoring never touches the cases
