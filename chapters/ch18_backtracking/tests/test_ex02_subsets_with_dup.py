import pytest


def test_examples(load):
    m = load("ex02_subsets_with_dup")
    assert sorted(m.solve([1, 2, 2])) == [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]


@pytest.mark.parametrize("nums, count", [([], 1), ([2, 2, 2], 4), ([4, 4, 1, 4], 8),
                                         ([1, 1, 2, 2, 3, 3, 3], 36)])
def test_counts_and_uniqueness(load, nums, count):
    m = load("ex02_subsets_with_dup")
    got = m.solve(nums)
    assert len(got) == count
    assert len({tuple(s) for s in got}) == count
    assert sorted(got) == m.brute_force(nums)
