import random

import pytest

NAME = "ex05_find_duplicate_floyd"


def _make(rng, n):
    """n + 1 values in 1..n where exactly one value repeats (2..n+1 copies)."""
    dup = rng.randint(1, n)
    copies = rng.randint(2, n + 1)
    others = rng.sample([v for v in range(1, n + 1) if v != dup], n + 1 - copies)
    nums = [dup] * copies + others
    rng.shuffle(nums)
    return nums, dup


def test_examples(load):
    m = load(NAME)
    assert m.solve([1, 3, 4, 2, 2]) == 2
    assert m.solve([3, 1, 3, 4, 2]) == 3
    assert (m.is_happy(19), m.is_happy(2)) == (True, False)


@pytest.mark.parametrize("nums, expected", [
    ([1, 1], 1), ([2, 2, 2, 2, 2], 2), ([4, 3, 1, 4, 2, 4], 4), ([2, 1, 2], 2),
])
def test_edge_cases(load, nums, expected):
    assert load(NAME).solve(nums) == expected


def test_does_not_mutate(load):
    nums = [3, 1, 3, 4, 2]
    load(NAME).solve(nums)
    assert nums == [3, 1, 3, 4, 2]


def test_random_all_rungs_agree(load):
    m = load(NAME)
    rng = random.Random(1005)
    for _ in range(400):
        nums, dup = _make(rng, rng.randint(1, 20))
        assert m.solve(nums) == dup
        assert m.brute_force(nums) == dup
        assert m.seen_set(nums) == dup
        assert m.count_binary_search(nums) == dup


def test_sum_formula_fails_with_many_copies(load):
    assert load(NAME).wrong_sum_formula([2, 2, 2, 2, 2]) != 2


def test_happy_floyd_matches_set(load):
    m = load(NAME)
    assert all(m.is_happy(x) == m.is_happy_set(x) for x in range(1, 3000))
    assert m.is_happy(1) and m.is_happy(7) and not m.is_happy(4)
