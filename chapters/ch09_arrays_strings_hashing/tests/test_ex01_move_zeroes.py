import random

import pytest


def test_examples(load):
    m = load("ex01_move_zeroes")
    assert m.solve([0, 1, 0, 3, 12]) == [1, 3, 12, 0, 0]
    assert m.solve([0]) == [0]


def test_in_place(load):
    m = load("ex01_move_zeroes")
    nums = [0, 2, 0, 1]
    assert m.solve(nums) is nums
    assert nums == [2, 1, 0, 0]


@pytest.mark.parametrize("nums, expected", [
    ([], []), ([1, 2], [1, 2]), ([0, 0], [0, 0]), ([0, -1, 0, 5], [-1, 5, 0, 0]),
])
def test_edge_cases(load, nums, expected):
    assert load("ex01_move_zeroes").solve(nums) == expected


def test_random_against_brute(load):
    m = load("ex01_move_zeroes")
    rng = random.Random(9)
    for _ in range(200):
        nums = [rng.choice([0, 0, 1, 2, -3]) for _ in range(rng.randint(0, 12))]
        assert m.solve(list(nums)) == m.brute_force(list(nums)) == m.bubble(list(nums))
