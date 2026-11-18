import pytest


def test_examples(load):
    m = load("ex07_combination_sum_ii")
    assert m.solve([10, 1, 2, 7, 6, 1, 5], 8) == [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]
    assert m.solve([2, 5, 2, 1, 2], 5) == [[1, 2, 2], [5]]
    assert m.solve([3], 2) == []


@pytest.mark.parametrize("cands, target", [([1, 1, 1, 2, 2, 3, 4, 5, 6, 6], 9), ([4, 4, 4], 8),
                                           ([1, 2, 3], 6)])
def test_matches_brute_force(load, cands, target):
    m = load("ex07_combination_sum_ii")
    assert m.solve(cands, target) == m.brute_force(cands, target)


def test_large_duplicate_input_is_fast(load):
    m = load("ex07_combination_sum_ii")
    got = m.solve([1] * 60 + [2] * 40, 10)
    assert got == [[1] * (10 - 2 * t) + [2] * t for t in range(6)]
