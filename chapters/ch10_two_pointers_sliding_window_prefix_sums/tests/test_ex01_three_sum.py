import random

import pytest

NAME = "ex01_three_sum"


def test_examples(load):
    m = load(NAME)
    assert m.solve([-1, 0, 1, 2, -1, -4]) == [(-1, -1, 2), (-1, 0, 1)]
    assert m.solve([0, 0, 0, 0]) == [(0, 0, 0)]


@pytest.mark.parametrize("nums, expected", [
    ([], []), ([0], []), ([0, 0], []), ([1, 2, 3], []), ([-2, 1, 1], [(-2, 1, 1)]),
    ([-2, 0, 1, 1, 2], [(-2, 0, 2), (-2, 1, 1)]),
])
def test_edge_cases(load, nums, expected):
    assert load(NAME).solve(nums) == expected


def test_does_not_mutate_input(load):
    nums = [3, -1, -2, 0]
    load(NAME).solve(nums)
    assert nums == [3, -1, -2, 0]


def test_random_all_rungs_agree(load):
    m = load(NAME)
    rng = random.Random(1001)
    for _ in range(300):
        nums = [rng.randint(-6, 6) for _ in range(rng.randint(0, 12))]
        expected = m.brute_force(nums)
        assert m.solve(nums) == expected
        assert m.hash_two_sum(nums) == expected


def test_wrong_lookahead_loses_triplets(load):
    m = load(NAME)
    assert m.wrong_lookahead_skip([-1, 0, 1, 2, -1, -4]) == [(-1, 0, 1)]
