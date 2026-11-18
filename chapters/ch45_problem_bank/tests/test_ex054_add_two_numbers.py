import random

import pytest

NAME = "ex054_add_two_numbers"


def test_examples(load):
    m = load(NAME)
    assert m.to_list(m.solve(m.build([2, 4, 3]), m.build([5, 6, 4]))) == [7, 0, 8]
    assert m.to_list(m.solve(m.build([9, 9, 9]), m.build([1]))) == [0, 0, 0, 1]
    assert m.to_list(m.solve(m.build([0]), m.build([0]))) == [0]


@pytest.mark.parametrize("a, b, expected", [
    ([5], [5], [0, 1]),
    ([1, 8], [0], [1, 8]),
    ([9, 9], [9], [8, 0, 1]),
])
def test_edge_cases(load, a, b, expected):
    m = load(NAME)
    assert m.to_list(m.solve(m.build(a), m.build(b))) == expected
    assert m.to_list(m.interview_version(m.build(a), m.build(b))) == expected


def test_random_matches_brute_force(load):
    m = load(NAME)
    rng = random.Random(54)
    for _ in range(300):
        x, y = rng.randint(0, 10**12), rng.randint(0, 10**6)
        a = [int(c) for c in reversed(str(x))]
        b = [int(c) for c in reversed(str(y))]
        got = m.to_list(m.solve(m.build(a), m.build(b)))
        assert got == m.to_list(m.brute_force(m.build(a), m.build(b)))
        assert got == [int(c) for c in reversed(str(x + y))]
