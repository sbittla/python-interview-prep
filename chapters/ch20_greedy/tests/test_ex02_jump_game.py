import random

import pytest


def test_examples(load):
    m = load("ex02_jump_game")
    assert m.can_reach([2, 3, 1, 1, 4]) is True
    assert m.can_reach([3, 2, 1, 0, 4]) is False
    assert m.min_jumps([2, 3, 1, 1, 4]) == 2


@pytest.mark.parametrize("nums, reach, jumps", [
    ([0], True, 0), ([1, 0], True, 1), ([0, 1], False, -1), ([2, 0, 0], True, 1), ([1, 1, 1, 1], True, 3),
])
def test_edge_cases(load, nums, reach, jumps):
    m = load("ex02_jump_game")
    assert m.can_reach(nums) is reach
    assert m.min_jumps(nums) == jumps


def test_random_against_dp(load):
    m = load("ex02_jump_game")
    rng = random.Random(2)
    for _ in range(300):
        nums = [rng.randint(0, 3) for _ in range(rng.randint(1, 12))]
        assert m.can_reach(nums) == m.can_reach_dp(nums)
        assert m.min_jumps(nums) == m.min_jumps_dp(nums)
