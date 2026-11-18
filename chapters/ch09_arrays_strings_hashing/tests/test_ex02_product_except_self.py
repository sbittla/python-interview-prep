import math
import random

import pytest


def test_examples(load):
    m = load("ex02_product_except_self")
    assert m.solve([1, 2, 3, 4]) == [24, 12, 8, 6]
    assert m.solve([2, 0, 5]) == [0, 10, 0]


@pytest.mark.parametrize("nums, expected", [
    ([0, 0], [0, 0]), ([5, 7], [7, 5]), ([-1, -2, -3], [6, 3, 2]), ([0, 4, 0], [0, 0, 0]),
])
def test_edge_cases(load, nums, expected):
    assert load("ex02_product_except_self").solve(nums) == expected


def test_random_against_brute(load):
    m = load("ex02_product_except_self")
    rng = random.Random(9)
    for _ in range(200):
        nums = [rng.randint(-3, 3) for _ in range(rng.randint(2, 8))]
        expected = [math.prod(nums[:i] + nums[i + 1:]) for i in range(len(nums))]
        assert m.solve(nums) == expected == m.brute_force(nums) == m.with_division(nums)
