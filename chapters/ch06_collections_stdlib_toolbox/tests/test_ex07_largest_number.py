import random

import pytest


def test_examples(load):
    m = load("ex07_largest_number")
    assert m.solve([10, 2]) == "210"
    assert m.solve([3, 30, 34, 5, 9]) == "9534330"
    assert m.solve([0, 0]) == "0"


@pytest.mark.parametrize("nums, expected", [
    ([0], "0"), ([1], "1"), ([3, 30, 34], "34330"), ([121, 12], "12121"),
    ([0, 0, 1], "100"), ([999999999, 9], "9999999999"), ([20, 1, 0], "2010"),
])
def test_edge_cases(load, nums, expected):
    assert load("ex07_largest_number").solve(nums) == expected


def test_lexicographic_is_wrong(load):
    m = load("ex07_largest_number")
    assert m.wrong_lexicographic([3, 30, 34]) != m.solve([3, 30, 34])


def test_random_against_brute(load):
    m = load("ex07_largest_number")
    rng = random.Random(7)
    for _ in range(300):
        nums = [rng.choice([0, 1, 3, 9, 10, 30, 34, 300, 121, 12]) for _ in range(rng.randint(1, 6))]
        assert m.solve(nums) == m.brute_force(nums)
