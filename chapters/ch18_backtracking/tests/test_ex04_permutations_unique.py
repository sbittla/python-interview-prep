from itertools import permutations

import pytest


def test_examples(load):
    m = load("ex04_permutations_unique")
    assert m.solve([1, 1, 2]) == [[1, 1, 2], [1, 2, 1], [2, 1, 1]]
    assert m.solve([7, 7, 7]) == [[7, 7, 7]]


@pytest.mark.parametrize("nums", [[], [1], [2, 1, 2], [1, 1, 2, 2, 3], [3, 3, 0, 3, 1]])
def test_distinct_and_complete(load, nums):
    m = load("ex04_permutations_unique")
    expected = [list(p) for p in sorted(set(permutations(nums)))]
    assert m.solve(nums) == expected
    assert m.solve_counter(nums) == expected
