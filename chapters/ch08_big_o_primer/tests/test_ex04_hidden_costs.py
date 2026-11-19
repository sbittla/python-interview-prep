import pytest


def test_examples(load):
    m = load("ex04_hidden_costs")
    assert m.eq_calls_for_lookups("list", 100, [-1]) == 100
    assert m.eq_calls_for_lookups("set", 100, [-1]) == 0
    assert (m.slice_copies(5), m.index_copies(5)) == (10, 0)


@pytest.mark.parametrize("n", [0, 1, 50, 300])
def test_list_scan_is_linear_set_is_constant(load, n):
    m = load("ex04_hidden_costs")
    misses = [-1, -2, -3]
    assert m.eq_calls_for_lookups("list", n, misses) == 3 * n
    assert m.eq_calls_for_lookups("set", n, misses) == 0


def test_hit_costs(load):
    m = load("ex04_hidden_costs")
    assert m.eq_calls_for_lookups("list", 10, [9]) == 10      # found at the end
    assert m.eq_calls_for_lookups("list", 10, [0]) == 1
    assert m.eq_calls_for_lookups("set", 10, [9]) == 1        # one == confirms the hit


@pytest.mark.parametrize("n, expected", [(0, 0), (1, 0), (2, 1), (10, 45), (300, 44850)])
def test_slice_and_drain_are_quadratic(load, n, expected):
    m = load("ex04_hidden_costs")
    assert m.slice_copies(n) == expected
    assert m.drain_front("list", n) == expected
    assert m.drain_front("deque", n) == 0
    assert m.index_copies(n) == 0
