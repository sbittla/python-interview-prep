import random

import pytest


def test_examples(load):
    m = load("ex04_next_greater_element")
    assert m.next_greater([2, 1, 2, 4, 3]) == [4, 2, 4, None, None]
    assert m.next_greater_circular([2, 1, 2, 4, 3]) == [4, 2, 4, None, 4]
    assert m.next_smaller([4, 1, 3, 2]) == [1, None, 2, None]


@pytest.mark.parametrize("nums, greater, circular", [
    ([], [], []),
    ([7], [None], [None]),
    ([1, 1, 1], [None, None, None], [None, None, None]),
    ([5, 4, 3], [None, None, None], [None, 5, 5]),
    ([1, 2, 3], [2, 3, None], [2, 3, None]),
    ([-1, -3, -2], [None, -2, None], [None, -2, -1]),
])
def test_edge_cases(load, nums, greater, circular):
    m = load("ex04_next_greater_element")
    assert m.next_greater(nums) == greater
    assert m.next_greater_circular(nums) == circular


def test_random_against_brute(load):
    m = load("ex04_next_greater_element")
    rng = random.Random(7)
    for _ in range(400):
        nums = [rng.randint(-4, 4) for _ in range(rng.randint(0, 12))]
        assert m.next_greater(nums) == m.brute_force(nums)
        assert m.next_greater_circular(nums) == m.brute_force_circular(nums)
        assert m.next_smaller(nums) == m.brute_force_smaller(nums)
