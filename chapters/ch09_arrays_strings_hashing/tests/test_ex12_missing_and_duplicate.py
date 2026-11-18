import random

import pytest


def test_examples(load):
    m = load("ex12_missing_and_duplicate")
    assert m.find_error([1, 2, 2, 4]) == (2, 3)
    assert m.solve([3, 4, -1, 1]) == 2
    assert m.solve([7, 8, 9]) == 1


@pytest.mark.parametrize("nums, expected", [([], 1), ([1], 2), ([2], 1), ([1, 1], 2), ([2, 1], 3), ([0, -1], 1)])
def test_edge_cases(load, nums, expected):
    assert load("ex12_missing_and_duplicate").solve(nums) == expected


def test_cyclic_sort(load):
    assert load("ex12_missing_and_duplicate").cyclic_sort([3, 1, 5, 4, 2]) == [1, 2, 3, 4, 5]


def test_random(load):
    m = load("ex12_missing_and_duplicate")
    rng = random.Random(12)
    for _ in range(300):
        nums = [rng.randint(-2, 8) for _ in range(rng.randint(0, 8))]
        assert m.solve(list(nums)) == m.brute_force(nums) == m.with_set(nums)
    for _ in range(100):
        n = rng.randint(2, 9)
        perm = list(range(1, n + 1))
        rng.shuffle(perm)
        i, j = rng.sample(range(n), 2)
        missing, dup = perm[i], perm[j]
        perm[i] = dup
        assert m.find_error(perm) == (dup, missing)
