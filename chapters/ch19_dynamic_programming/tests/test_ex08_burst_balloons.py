import random

import pytest

M = "ex08_burst_balloons"


def test_examples(load):
    m = load(M)
    assert m.max_coins([3, 1, 5, 8]) == 167
    assert (m.max_coins([1, 5]), m.max_coins([])) == (10, 0)


@pytest.mark.parametrize("nums, expected", [
    ([], 0), ([7], 7), ([1, 5], 10), ([0, 0], 0), ([2, 4, 3, 5, 1, 6], 276),
])
def test_edges(load, nums, expected):
    m = load(M)
    assert m.max_coins(nums) == m.max_coins_memo(nums) == expected
    assert m.max_coins_subset_memo(nums) == m.max_coins_brute(nums) == expected


def test_random_against_brute(load):
    m = load(M)
    rng = random.Random(29)
    for _ in range(80):
        nums = [rng.randint(0, 9) for _ in range(rng.randint(0, 6))]
        expected = m.max_coins_brute(nums)
        assert m.max_coins(nums) == m.max_coins_memo(nums) == m.max_coins_subset_memo(nums) == expected


def test_larger_input_top_down_equals_bottom_up(load):
    m = load(M)
    nums = [(i * 37) % 100 + 1 for i in range(60)]
    assert m.max_coins(nums) == m.max_coins_memo(nums)
