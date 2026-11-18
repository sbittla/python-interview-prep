import random

import pytest

NAME = "ex053_reorder_list"


def test_examples(load):
    m = load(NAME)
    assert m.reordered([1, 2, 3, 4]) == [1, 4, 2, 3]
    assert m.reordered([1, 2, 3, 4, 5]) == [1, 5, 2, 4, 3]
    assert m.reordered([]) == []


@pytest.mark.parametrize("values, expected", [([1], [1]), ([1, 2], [1, 2]), ([1, 2, 3], [1, 3, 2])])
def test_edge_cases(load, values, expected):
    m = load(NAME)
    assert m.reordered(values) == expected
    assert m.reordered(values, m.interview_version) == expected


def test_random_matches_brute_force(load):
    m = load(NAME)
    rng = random.Random(53)
    for _ in range(200):
        values = [rng.randint(0, 99) for _ in range(rng.randint(0, 25))]
        expected = m.reordered(values, m.brute_force)
        assert m.reordered(values) == expected
        assert m.reordered(values, m.interview_version) == expected
