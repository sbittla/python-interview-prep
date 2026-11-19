import random

import pytest

NAME = "ex10_subarray_sum_k"


def test_examples(load):
    m = load(NAME)
    assert m.solve([1, 1, 1], 2) == 2
    assert m.solve([3, 4, -7, 3, 1, 3, 1, -4], 7) == 3
    assert m.longest([1, -1, 5, -2, 3], 3) == 4


@pytest.mark.parametrize("nums, k, count, longest", [
    ([], 5, 0, 0), ([5], 5, 1, 1), ([0, 0, 0], 0, 6, 3), ([1, -1, 1, -1], 0, 4, 4),
    ([1, 2, 3], 7, 0, 0), ([-1, -1, 1], -1, 3, 3),
])
def test_edge_cases(load, nums, k, count, longest):
    m = load(NAME)
    assert m.solve(nums, k) == count
    assert m.longest(nums, k) == longest


def test_random_all_rungs_agree(load):
    m = load(NAME)
    rng = random.Random(1010)
    for _ in range(400):
        nums = [rng.randint(-3, 3) for _ in range(rng.randint(0, 14))]
        k = rng.randint(-4, 4)
        want = m.brute_force(nums, k)
        assert m.solve(nums, k) == m.running_sum(nums, k) == want
        assert m.longest(nums, k) == m.longest_brute(nums, k)


def test_sliding_window_ok_for_positive_only(load):
    m = load(NAME)
    rng = random.Random(10100)
    for _ in range(300):
        nums = [rng.randint(1, 5) for _ in range(rng.randint(0, 14))]
        k = rng.randint(1, 12)
        assert m.wrong_sliding_window(nums, k) == m.solve(nums, k)


def test_sliding_window_wrong_with_negatives_and_zeros(load):
    m = load(NAME)
    assert m.wrong_sliding_window([1, -1, 1, -1], 0) != m.solve([1, -1, 1, -1], 0)
    assert m.wrong_sliding_window([0, 0, 0], 0) != m.solve([0, 0, 0], 0)
