import pytest


def test_examples(load):
    m = load("ex01_subsets")
    assert sorted(m.solve([1, 2, 3])) == [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
    assert m.solve([]) == [[]]


@pytest.mark.parametrize("nums", [[5], [0, 1], [3, 1, 2], list(range(8))])
def test_matches_brute_force(load, nums):
    m = load("ex01_subsets")
    got = m.solve(nums)
    assert len(got) == 2 ** len(nums)
    assert sorted(got) == sorted(m.brute_force(nums))


def test_results_are_independent_copies(load):
    m = load("ex01_subsets")
    got = m.solve([1, 2])
    got[0].append(99)
    assert [99] not in got[1:]
