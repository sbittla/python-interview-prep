import random

import pytest

NAME = "ex03_remove_duplicates_in_place"


def _expected(nums, k):
    out = []
    for x in nums:
        if out.count(x) < k:
            out.append(x)
    return out


def test_examples(load):
    m = load(NAME)
    a = [1, 1, 1, 2, 2, 3]
    assert a[:m.solve(a, 2)] == [1, 1, 2, 2, 3]
    b = [0, 0, 1, 1, 1, 2]
    assert b[:m.solve(b, 1)] == [0, 1, 2]


@pytest.mark.parametrize("nums, k, expected", [
    ([], 1, []), ([7], 3, [7]), ([2, 2, 2, 2], 1, [2]), ([1, 2, 3], 1, [1, 2, 3]),
    ([5, 5, 5], 5, [5, 5, 5]),
])
def test_edge_cases(load, nums, k, expected):
    a = list(nums)
    m = load(NAME).solve(a, k)
    assert a[:m] == expected


def test_in_place_keeps_list_length(load):
    a = [1, 1, 2]
    load(NAME).solve(a, 1)
    assert len(a) == 3                    # nothing appended or deleted: truly in place


def test_random_all_rungs_agree(load):
    m = load(NAME)
    rng = random.Random(1003)
    for _ in range(400):
        nums = sorted(rng.randint(0, 5) for _ in range(rng.randint(0, 14)))
        k = rng.randint(1, 3)
        want = _expected(nums, k)
        a = list(nums)
        assert a[:m.solve(a, k)] == want
        b = list(nums)
        assert b[:m.copy_filter(b, k)] == want
        c = list(nums)
        assert c[:m.brute_force(c, k)] == want


def test_read_side_comparison_is_wrong(load):
    m = load(NAME)
    a = [1, 1, 1, 2, 2]
    assert a[:m.wrong_read_side(a, 2)] == [1, 1, 2]
