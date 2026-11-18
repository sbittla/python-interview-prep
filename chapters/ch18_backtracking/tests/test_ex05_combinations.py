from itertools import combinations
from math import comb

import pytest


def test_examples(load):
    m = load("ex05_combinations")
    assert m.solve(4, 2) == [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
    assert m.solve(3, 0) == [[]]
    assert m.solve(3, 3) == [[1, 2, 3]]


@pytest.mark.parametrize("n, k", [(1, 1), (5, 3), (8, 4), (12, 10)])
def test_against_itertools(load, n, k):
    m = load("ex05_combinations")
    got = m.solve(n, k)
    assert got == [list(c) for c in combinations(range(1, n + 1), k)]
    assert len(got) == comb(n, k)


def test_pruning_reduces_calls(load):
    m = load("ex05_combinations")
    a, b = {}, {}
    assert m.solve(15, 12, prune=False, stats=a) == m.solve(15, 12, prune=True, stats=b)
    assert b["calls"] < a["calls"]
