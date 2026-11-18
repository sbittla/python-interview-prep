import pytest


def test_examples(load):
    m = load("ex06_combination_sum")
    assert m.solve([2, 3, 6, 7], 7) == [[2, 2, 3], [7]]
    assert m.solve([2, 3, 5], 8) == [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
    assert m.solve([2], 1) == []


@pytest.mark.parametrize("cands, target", [([7, 3, 2], 18), ([5, 10, 25], 50), ([4, 6], 3)])
def test_matches_brute_force(load, cands, target):
    m = load("ex06_combination_sum")
    got = m.solve(cands, target)
    assert got == m.brute_force(cands, target)
    assert all(sum(c) == target for c in got)
