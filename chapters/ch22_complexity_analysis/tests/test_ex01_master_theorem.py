import math

import pytest


def test_examples(load):
    m = load("ex01_master_theorem")
    assert m.master(2, 2, 1, 0) == (2, "n log n")
    assert m.master(3, 2, 1, 0) == (1, "n^1.585")
    assert m.master(2, 2, 2, 0) == (3, "n^2")


@pytest.mark.parametrize("args, expected", [
    ((1, 2, 0, 0), (2, "log n")),            # binary search
    ((7, 2, 2, 0), (1, "n^2.807")),          # Strassen
    ((2, 2, 1, 1), (2, "n log^2 n")),        # extended case 2
    ((4, 2, 2, 0), (2, "n^2 log n")),
    ((1, 2, 1, 0), (3, "n")),                # T(n/2) + n: geometric, root wins
    ((2, 4, 0, 0), (1, "n^0.500")),
    ((8, 2, 3, 2), (2, "n^3 log^3 n")),
    ((2, 2, 0, 0), (1, "n")),                # tree traversal
])
def test_cases(load, args, expected):
    assert load("ex01_master_theorem").master(*args) == expected


@pytest.mark.parametrize("bad", [(2, 2, 1, -1), (1, 1, 0, 0), (0, 2, 1, 0), (2, 2, -1, 0), (2, 2, 1, 0.5)])
def test_invalid(load, bad):
    with pytest.raises(ValueError):
        load("ex01_master_theorem").master(*bad)


def test_evaluate_exact(load):
    m = load("ex01_master_theorem")
    # merge sort with T(1) = 1: T(2^j) = 2^j * (j + 1)
    for j in range(0, 12):
        assert m.evaluate(2, 2, 1, 0, 2 ** j) == 2 ** j * (j + 1)
    assert m.evaluate(1, 2, 0, 0, 1024) == 11            # binary search: log2 n + 1


def test_level_costs(load):
    m = load("ex01_master_theorem")
    assert m.level_costs(2, 2, 1, 0, 8) == [8, 8, 8, 8]   # every level costs n
    assert m.level_costs(3, 2, 1, 0, 16) == [16, 24, 36, 54, 81]   # grows by a/b^c = 1.5
    assert sum(m.level_costs(3, 2, 1, 0, 64)) == m.evaluate(3, 2, 1, 0, 64)


@pytest.mark.parametrize("args", [(1, 2, 0, 0), (2, 2, 1, 0), (3, 2, 1, 0), (2, 2, 1, 1), (2, 2, 2, 0)])
def test_claimed_bound_is_tight(load, args):
    assert load("ex01_master_theorem").ratio_spread(*args) < 1.3


def test_wrong_bound_detected(load):
    m = load("ex01_master_theorem")
    assert m.ratio_spread(3, 2, 1, 0, g=lambda n: n * math.log2(n)) > m.TIGHT
    assert m.ratio_spread(2, 2, 1, 0, g=lambda n: n) > m.TIGHT        # merge sort is not O(n)
    assert m.ratio_spread(2, 2, 1, 1, g=lambda n: n * math.log2(n)) > m.TIGHT   # needs log^2
