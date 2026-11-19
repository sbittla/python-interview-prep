import random
from collections import Counter

import pytest

NAME = "ex04_dutch_flag_partition"


def _check(original, arranged, pivot, bounds):
    lt, gt = bounds
    assert Counter(original) == Counter(arranged)
    assert all(x < pivot for x in arranged[:lt])
    assert all(x == pivot for x in arranged[lt:gt])
    assert all(x > pivot for x in arranged[gt:])


def test_examples(load):
    m = load(NAME)
    a = [2, 0, 2, 1, 1, 0]
    assert m.solve(a, 1) == (2, 4)
    assert a == [0, 0, 1, 1, 2, 2]


@pytest.mark.parametrize("nums, pivot", [
    ([], 0), ([5], 9), ([5], 1), ([3, 3, 3], 3), ([1, 2, 0], 1), ([2, 1, 0], 1), ([0, 0, 2, 2], 1),
])
def test_edge_cases(load, nums, pivot):
    a = list(nums)
    _check(nums, a, pivot, load(NAME).solve(a, pivot))


def test_random_all_rungs(load):
    m = load(NAME)
    rng = random.Random(1004)
    for _ in range(400):
        nums = [rng.randint(-3, 3) for _ in range(rng.randint(0, 15))]
        pivot = rng.randint(-4, 4)
        for fn in (m.solve, m.two_pass, m.brute_force):
            a = list(nums)
            _check(nums, a, pivot, fn(a, pivot))


def test_advancing_after_right_swap_is_wrong(load):
    a = [1, 2, 0]
    load(NAME).wrong_advance_after_swap(a, 1)
    assert a == [1, 0, 2]
