from itertools import permutations

import pytest


def test_examples(load):
    m = load("ex03_permutations")
    assert m.solve([1, 2, 3]) == [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
    assert m.solve([]) == [[]]


@pytest.mark.parametrize("nums", [[1], [0, 1], [4, 2, 9, 1], list(range(6))])
def test_against_itertools(load, nums):
    m = load("ex03_permutations")
    assert m.solve(nums) == [list(p) for p in permutations(nums)]
    assert sorted(m.solve_swap(nums)) == sorted(m.solve(nums))
