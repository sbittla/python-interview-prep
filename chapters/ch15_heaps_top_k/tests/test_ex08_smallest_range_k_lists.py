import random

import pytest


def test_examples(load):
    m = load("ex08_smallest_range_k_lists")
    assert m.solve([[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]) == (20, 24)
    assert m.solve([[1, 2, 3], [1, 2, 3], [1, 2, 3]]) == (1, 1)


@pytest.mark.parametrize("lists, expected", [
    ([[5]], (5, 5)),
    ([[-5, -1], [10]], (-1, 10)),
    ([[1, 9], [4, 12], [7, 10, 16]], (9, 12)),
    ([[1, 5], [3, 7]], (1, 3)),                         # widths tie: (1,3),(3,5),(5,7) -> smallest lo
])
def test_edge_cases(load, lists, expected):
    m = load("ex08_smallest_range_k_lists")
    for fn in (m.solve, m.brute_force, m.by_window):
        assert fn(lists) == expected


@pytest.mark.parametrize("bad", [[], [[1], []]])
def test_invalid_input_same_in_every_rung(load, bad):
    m = load("ex08_smallest_range_k_lists")
    for fn in (m.solve, m.brute_force, m.by_window):
        with pytest.raises(ValueError):
            fn(bad)


def test_random_vs_brute(load):
    m = load("ex08_smallest_range_k_lists")
    rng = random.Random(10)
    for _ in range(500):
        lists = [sorted(rng.randint(0, 12) for _ in range(rng.randint(1, 5)))
                 for _ in range(rng.randint(1, 4))]
        expected = m.brute_force(lists)
        lo, hi = expected
        assert all(any(lo <= v <= hi for v in lst) for lst in lists)
        assert m.solve(lists) == m.by_window(lists) == expected
