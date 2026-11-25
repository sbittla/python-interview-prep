import random

import pytest

M = "ex02_house_robber"


def test_examples(load):
    m = load(M)
    assert m.rob([2, 7, 9, 3, 1]) == 12
    assert m.rob_with_houses([2, 7, 9, 3, 1]) == (12, [0, 2, 4])
    assert (m.rob_circular([2, 3, 2]), m.rob_circular([1, 2, 3, 1])) == (3, 4)


@pytest.mark.parametrize("nums, expected", [
    ([], 0), ([5], 5), ([5, 9], 9), ([2, 1, 1, 2], 4), ([0, 0, 0], 0), ([1, 2, 3, 1], 4),
])
def test_rob_edges(load, nums, expected):
    m = load(M)
    assert m.rob(nums) == m.rob_table(nums) == m.rob_memo(nums) == m.rob_brute(nums) == expected


def _check_houses(nums, total, houses):
    assert houses == sorted(houses)
    assert all(b - a >= 2 for a, b in zip(houses, houses[1:])), "adjacent houses robbed"
    assert sum(nums[i] for i in houses) == total


def test_rob_with_houses_random(load):
    m = load(M)
    rng = random.Random(2)
    for _ in range(300):
        nums = [rng.randint(0, 9) for _ in range(rng.randint(0, 12))]
        total, houses = m.rob_with_houses(nums)
        assert total == m.rob_brute(nums) == m.rob(nums)
        _check_houses(nums, total, houses)


@pytest.mark.parametrize("nums, expected", [
    ([7], 7), ([3, 9], 9), ([1, 2, 3], 3), ([200, 3, 140, 20, 10], 340),
])
def test_rob_circular_edges(load, nums, expected):
    m = load(M)
    assert m.rob_circular(nums) == m.rob_circular_brute(nums) == expected


def test_rob_circular_empty(load):
    assert load(M).rob_circular([]) == 0


def test_rob_circular_random(load):
    m = load(M)
    rng = random.Random(3)
    for _ in range(300):
        nums = [rng.randint(0, 9) for _ in range(rng.randint(1, 11))]
        assert m.rob_circular(nums) == m.rob_circular_brute(nums)
        assert m.rob_circular(nums) <= m.rob(nums)


def test_rob_long_row(load):
    m = load(M)
    assert m.rob([1] * 100_000) == 50_000
