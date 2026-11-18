import random

import pytest

NAME = "ex052_remove_nth_from_end"


def test_examples(load):
    m = load(NAME)
    assert m.to_list(m.solve(m.build([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
    assert m.solve(m.build([1]), 1) is None
    assert m.to_list(m.solve(m.build([1, 2]), 2)) == [2]


@pytest.mark.parametrize("values, k, expected", [
    ([1, 2], 1, [1]),
    ([1, 2, 3], 3, [2, 3]),
    ([4, 4, 4], 2, [4, 4]),
])
def test_edge_cases(load, values, k, expected):
    m = load(NAME)
    assert m.to_list(m.solve(m.build(values), k)) == expected
    assert m.to_list(m.interview_version(m.build(values), k)) == expected


def test_random_matches_brute_force(load):
    m = load(NAME)
    rng = random.Random(52)
    for _ in range(300):
        values = [rng.randint(0, 9) for _ in range(rng.randint(1, 15))]
        k = rng.randint(1, len(values))
        expected = values[: len(values) - k] + values[len(values) - k + 1:]
        assert m.to_list(m.solve(m.build(values), k)) == expected
        assert m.to_list(m.brute_force(m.build(values), k)) == expected
