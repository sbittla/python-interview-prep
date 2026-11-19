import heapq
import random

import pytest


def test_examples(load):
    m = load("ex10_top_k_quickselect")
    assert m.solve([3, 1, 4, 1, 5, 9, 2, 6], 3) == [9, 6, 5]
    assert m.solve([2, 2, 2, 1], 2) == [2, 2]


@pytest.mark.parametrize("nums, k, expected", [
    ([], 0, []), ([5], 1, [5]), ([7, -1, 7, 3], 0, []),
    ([-3, -1, -2], 3, [-1, -2, -3]), ([4, 4, 4, 4], 3, [4, 4, 4]),
])
def test_edge_cases(load, nums, k, expected):
    m = load("ex10_top_k_quickselect")
    for fn in (m.solve, m.by_sort, m.by_heap, m.by_quickselect):
        assert fn(nums, k) == expected


def test_does_not_mutate_input(load):
    m = load("ex10_top_k_quickselect")
    nums = [5, 1, 4, 2, 3]
    m.solve(nums, 2)
    assert nums == [5, 1, 4, 2, 3]


def test_random_vs_sort(load):
    m = load("ex10_top_k_quickselect")
    rng = random.Random(12)
    for _ in range(500):
        nums = [rng.randint(-4, 4) for _ in range(rng.randint(0, 30))]
        k = rng.randint(0, len(nums))
        expected = sorted(nums, reverse=True)[:k]
        assert m.by_heap(nums, k) == expected == heapq.nlargest(k, nums)
        for seed in (0, 1, 2):
            assert m.by_quickselect(nums, k, seed) == expected
