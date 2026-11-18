import random

import pytest


def test_examples(load):
    m = load("ex05_two_sum")
    assert m.solve([2, 7, 11, 15], 9) == (0, 1)
    assert m.solve([3, 3], 6) == (0, 1)
    assert m.solve([1, 2], 7) is None


@pytest.mark.parametrize("nums, target, expected", [
    ([], 0, None), ([5], 10, None), ([3, 2, 4], 6, (1, 2)), ([-3, 4, 3, 90], 0, (0, 2)), ([0, 0], 0, (0, 1)),
])
def test_edge_cases(load, nums, target, expected):
    assert load("ex05_two_sum").solve(nums, target) == expected


def test_random_against_brute(load):
    m = load("ex05_two_sum")
    rng = random.Random(5)
    for _ in range(300):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(0, 10))]
        target = rng.randint(-6, 6)
        assert m.solve(nums, target) == m.brute_force(nums, target)
        pair = m.sort_two_pointers(nums, target)
        if pair is None:
            assert m.brute_force(nums, target) is None
        else:
            i, j = pair
            assert i < j and nums[i] + nums[j] == target
