import random

import pytest

NAME = "ex06_max_average_window"


def test_examples(load):
    m = load(NAME)
    assert m.solve([1, 12, -5, -6, 50, 3], 4) == 51
    assert m.max_average([1, 12, -5, -6, 50, 3], 4) == 12.75
    assert m.window_maxima([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]


@pytest.mark.parametrize("nums, k, expected", [
    ([5], 1, 5), ([-3, -1, -2], 2, -3), ([4, 0, 4, 3, 3], 5, 14), ([-1], 1, -1), ([0, 0, 0], 2, 0),
])
def test_edge_cases(load, nums, k, expected):
    assert load(NAME).solve(nums, k) == expected


def test_window_maxima_edges(load):
    m = load(NAME)
    assert m.window_maxima([4], 1) == [4]
    assert m.window_maxima([2, 2, 2], 2) == [2, 2]
    assert m.window_maxima([5, 4, 3, 2], 4) == [5]


def test_random_all_rungs_agree(load):
    m = load(NAME)
    rng = random.Random(1006)
    for _ in range(400):
        n = rng.randint(1, 15)
        nums = [rng.randint(-9, 9) for _ in range(n)]
        k = rng.randint(1, n)
        assert m.solve(nums, k) == m.brute_force(nums, k) == m.prefix_sums(nums, k)
        assert m.window_maxima(nums, k) == m.window_maxima_brute(nums, k)


def test_zero_init_wrong_on_all_negative(load):
    assert load(NAME).wrong_zero_init([-3, -1, -2], 2) == 0


def test_off_by_one_misses_last_window(load):
    m = load(NAME)
    assert m.wrong_off_by_one([1, 2, 9], 2) == 3 and m.solve([1, 2, 9], 2) == 11


@pytest.mark.parametrize("k", [0, 4, -1])
def test_invalid_k_raises(load, k):
    with pytest.raises(ValueError):
        load(NAME).solve([1, 2, 3], k)
