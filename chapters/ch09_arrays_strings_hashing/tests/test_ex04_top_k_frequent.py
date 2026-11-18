import random
from collections import Counter

import pytest


def test_examples(load):
    m = load("ex04_top_k_frequent")
    assert m.solve([1, 1, 1, 2, 2, 3], 2) == [1, 2]
    assert m.solve([4, 4, 5, 5, 6], 2) == [4, 5]


@pytest.mark.parametrize("nums, k, expected", [
    ([7], 1, [7]), ([3, 2, 1], 3, [1, 2, 3]), ([-1, -1, 2, 2, 3], 1, [-1]),
])
def test_edge_cases(load, nums, k, expected):
    assert load("ex04_top_k_frequent").solve(nums, k) == expected


def test_random_all_methods(load):
    m = load("ex04_top_k_frequent")
    rng = random.Random(4)
    for _ in range(200):
        nums = [rng.randint(-3, 5) for _ in range(rng.randint(1, 15))]
        k = rng.randint(1, len(set(nums)))
        c = Counter(nums)
        expected = sorted(c, key=lambda v: (-c[v], v))[:k]
        assert m.solve(nums, k) == expected
        assert m.brute_force(nums, k) == expected
        assert m.by_sort(nums, k) == expected
        assert m.by_heap(nums, k) == expected
