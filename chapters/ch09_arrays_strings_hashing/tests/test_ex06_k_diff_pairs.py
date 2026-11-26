import random

import pytest


def test_examples(load):
    m = load("ex06_k_diff_pairs")
    assert m.solve([3, 1, 4, 1, 5], 2) == 2
    assert m.solve([1, 3, 1, 5, 4], 0) == 1


@pytest.mark.parametrize("nums, k, expected", [
    ([], 1, 0), ([1, 2, 3], 0, 0), ([1, 1, 1], 0, 1), ([1, 2, 3, 4, 5], 1, 4), ([-1, -3, 1], 2, 2),
])
def test_edge_cases(load, nums, k, expected):
    assert load("ex06_k_diff_pairs").solve(nums, k) == expected


def test_random_against_brute(load):
    m = load("ex06_k_diff_pairs")
    rng = random.Random(6)
    for _ in range(300):
        nums = [rng.randint(-4, 4) for _ in range(rng.randint(0, 10))]
        k = rng.randint(0, 4)
        assert m.solve(nums, k) == m.brute_force(nums, k)


def test_set_only_shortcut_is_wrong_for_k0(load):
    m = load("ex06_k_diff_pairs")
    assert m.wrong_set_only([1, 2, 3], 0) == 3          # counts every value
    assert m.solve([1, 2, 3], 0) == 0                    # no value repeats
