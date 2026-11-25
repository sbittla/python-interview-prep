import math

import pytest


def test_examples(load):
    m = load("ex04_recursion_tree_counter")
    assert m.subset_tree(3) == (15, 8, 12)
    assert m.perm_tree(3) == (16, 6, 18)
    assert m.fib_calls(5) == 15


@pytest.mark.parametrize("n", range(0, 13))
def test_subset_closed_form(load, n):
    m = load("ex04_recursion_tree_counter")
    assert m.subset_tree(n) == (2 ** (n + 1) - 1, 2 ** n, n * 2 ** (n - 1) if n else 0)


@pytest.mark.parametrize("n", range(0, 8))
def test_perm_closed_form(load, n):
    m = load("ex04_recursion_tree_counter")
    calls, leaves, copied = m.perm_tree(n)
    assert calls == m.perm_nodes_formula(n)
    assert leaves == math.factorial(n) and copied == n * math.factorial(n)
    if n >= 1:
        assert calls == math.floor(math.e * math.factorial(n))


@pytest.mark.parametrize("n", [0, 1, 2, 10, 20])
def test_fib_calls(load, n):
    m = load("ex04_recursion_tree_counter")
    assert m.fib_calls(n) == 2 * m.fibonacci(n + 1) - 1


@pytest.mark.parametrize("n, expected", [(0, 1), (1, 1), (2, 3), (5, 9), (50, 99)])
def test_memo_fib_calls(load, n, expected):
    assert load("ex04_recursion_tree_counter").memo_fib_calls(n) == expected


def test_fib_growth_is_phi_not_two(load):
    m = load("ex04_recursion_tree_counter")
    ratio = m.fib_calls(22) / m.fib_calls(21)
    assert abs(ratio - (1 + 5 ** 0.5) / 2) < 1e-3
