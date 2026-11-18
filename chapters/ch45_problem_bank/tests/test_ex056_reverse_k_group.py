import random

import pytest

NAME = "ex056_reverse_k_group"


def test_examples(load):
    m = load(NAME)
    assert m.to_list(m.solve(m.build([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
    assert m.to_list(m.solve(m.build([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
    assert m.to_list(m.solve(m.build([1, 2, 3]), 1)) == [1, 2, 3]


@pytest.mark.parametrize("values, k, expected", [
    ([], 3, []),
    ([1, 2], 5, [1, 2]),
    ([1, 2, 3], 3, [3, 2, 1]),
    ([1, 2, 3, 4], 2, [2, 1, 4, 3]),
])
def test_edge_cases(load, values, k, expected):
    m = load(NAME)
    assert m.to_list(m.solve(m.build(values), k)) == expected
    assert m.to_list(m.interview_version(m.build(values), k)) == expected


def test_random_matches_brute_force(load):
    m = load(NAME)
    rng = random.Random(56)
    for _ in range(300):
        values = [rng.randint(0, 9) for _ in range(rng.randint(0, 20))]
        k = rng.randint(1, 7)
        expected = m.to_list(m.brute_force(m.build(values), k))
        assert m.to_list(m.solve(m.build(values), k)) == expected
        assert m.to_list(m.interview_version(m.build(values), k)) == expected
