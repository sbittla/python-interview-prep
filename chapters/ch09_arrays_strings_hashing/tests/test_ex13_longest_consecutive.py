import random

import pytest


def test_examples(load):
    m = load("ex13_longest_consecutive")
    assert m.solve([100, 4, 200, 1, 3, 2]) == 4
    assert m.solve([]) == 0


@pytest.mark.parametrize("nums, expected", [([5], 1), ([1, 1, 1], 1), ([1, 2, 0, 1], 3), ([-2, -1, 9], 2)])
def test_edge_cases(load, nums, expected):
    assert load("ex13_longest_consecutive").solve(nums) == expected


def test_duplicates(load):
    m = load("ex13_longest_consecutive")
    assert m.contains_duplicate([1, 2, 3, 1]) is True
    assert m.contains_duplicate([]) is False
    assert m.first_duplicate([2, 5, 1, 5, 2]) == 5
    assert m.first_duplicate([1, 2]) is None


def test_random(load):
    m = load("ex13_longest_consecutive")
    rng = random.Random(13)
    for _ in range(300):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(0, 10))]
        assert m.solve(nums) == m.brute_force(nums) == m.by_sorting(nums)
