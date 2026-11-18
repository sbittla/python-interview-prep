import random

import pytest

NAME = "ex050_merge_two_sorted_lists"


def test_examples(load):
    m = load(NAME)
    assert m.to_list(m.solve(m.build([1, 3, 5]), m.build([2, 3, 6]))) == [1, 2, 3, 3, 5, 6]
    assert m.to_list(m.solve(m.build([]), m.build([0]))) == [0]
    assert m.solve(None, None) is None


@pytest.mark.parametrize("a, b", [([], []), ([1], []), ([], [1]), ([5, 6], [1, 2]), ([1, 1], [1, 1])])
def test_edge_cases(load, a, b):
    m = load(NAME)
    assert m.to_list(m.solve(m.build(a), m.build(b))) == sorted(a + b)
    assert m.to_list(m.interview_version(m.build(a), m.build(b))) == sorted(a + b)


def test_stable_on_ties(load):
    m = load(NAME)
    a, b = m.build([1, 2]), m.build([1, 2])
    first_a = a
    assert m.solve(a, b) is first_a


def test_random_matches_brute_force(load):
    m = load(NAME)
    rng = random.Random(50)
    for _ in range(300):
        a = sorted(rng.randint(-9, 9) for _ in range(rng.randint(0, 10)))
        b = sorted(rng.randint(-9, 9) for _ in range(rng.randint(0, 10)))
        got = m.to_list(m.solve(m.build(a), m.build(b)))
        assert got == m.to_list(m.brute_force(m.build(a), m.build(b)))
