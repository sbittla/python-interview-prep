import random

import pytest

M = "ex05_lis"


def _is_increasing_subsequence(seq, nums):
    if any(a >= b for a, b in zip(seq, seq[1:])):
        return False
    it = iter(nums)
    return all(any(x == y for y in it) for x in seq)    # consumes nums in order


def test_examples(load):
    m = load(M)
    assert m.lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert m.lis([10, 9, 2, 5, 3, 7, 101, 18]) == [2, 3, 7, 18]
    assert (m.lis([7, 7, 7]), m.lis([])) == ([7], [])


@pytest.mark.parametrize("nums, length", [
    ([], 0), ([4], 1), ([7, 7, 7], 1), ([5, 4, 3], 1), ([1, 2, 3, 4], 4),
    ([0, 1, 0, 3, 2, 3], 4), ([-3, -1, -2, 0], 3), ([1, 1, 2, 2, 3, 3], 3),
])
def test_edges(load, nums, length):
    m = load(M)
    assert m.lis_length(nums) == m.lis_brute(nums) == m.lis_memo(nums) == length
    for seq in (m.lis(nums), m.lis_quadratic(nums)):
        assert len(seq) == length and _is_increasing_subsequence(seq, nums)


def test_tails_is_not_the_answer(load):
    m = load(M)
    assert m.lis([3, 4, 1]) == [3, 4]          # tails would read [1, 4]


def test_random_against_brute(load):
    m = load(M)
    rng = random.Random(11)
    for _ in range(300):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(0, 12))]
        length = m.lis_brute(nums)
        assert m.lis_memo(nums) == m.lis_length(nums) == length
        for seq in (m.lis(nums), m.lis_quadratic(nums)):
            assert len(seq) == length and _is_increasing_subsequence(seq, nums)


def test_large_input_fast_path(load):
    m = load(M)
    nums = list(range(50_000)) + list(range(50_000, 0, -1))
    assert m.lis_length(nums) == 50_001          # 0..49999 then 50000
