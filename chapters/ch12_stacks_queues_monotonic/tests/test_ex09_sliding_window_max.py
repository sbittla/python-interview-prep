import random

import pytest


def test_examples(load):
    m = load("ex09_sliding_window_max")
    assert m.max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]


@pytest.mark.parametrize("nums, k, expected", [
    ([], 3, []), ([4], 1, [4]), ([1, 2, 3], 1, [1, 2, 3]), ([1, 2, 3], 3, [3]),
    ([4, 4, 4, 1], 2, [4, 4, 4]), ([9, 8, 7, 6], 2, [9, 8, 7]), ([-5, -1, -3], 2, [-1, -1]),
])
def test_edge_cases(load, nums, k, expected):
    m = load("ex09_sliding_window_max")
    assert m.max_sliding_window(nums, k) == expected
    assert m.with_heap(nums, k) == expected


@pytest.mark.parametrize("k", [0, -1, 4])
def test_bad_window(load, k):
    with pytest.raises(ValueError):
        load("ex09_sliding_window_max").max_sliding_window([1, 2, 3], k)


def test_random_against_brute(load):
    m = load("ex09_sliding_window_max")
    rng = random.Random(23)
    for _ in range(400):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(1, 15))]
        k = rng.randint(1, len(nums))
        assert m.max_sliding_window(nums, k) == m.with_heap(nums, k) == m.brute_force(nums, k)
