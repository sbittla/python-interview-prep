import pytest


def test_examples(load):
    m = load("ex05_call_stack_space")
    assert m.sum_linear([1, 2, 3]) == (6, 4)
    assert m.sum_halves(list(range(8))) == (28, 4)
    assert m.sum_loop([5, 5]) == (10, 0)


@pytest.mark.parametrize("n, halves_depth", [(0, 1), (1, 1), (2, 2), (3, 3), (8, 4), (9, 5), (1024, 11)])
def test_depths(load, n, halves_depth):
    m = load("ex05_call_stack_space")
    xs = list(range(n))
    expected_sum = n * (n - 1) // 2
    assert m.sum_halves(xs) == (expected_sum, halves_depth)
    assert m.sum_loop(xs) == (expected_sum, 0)
    if n < 500:
        assert m.sum_linear(xs) == (expected_sum, n + 1)


def test_negative_values(load):
    m = load("ex05_call_stack_space")
    xs = [-5, 3, -1, 7]
    assert m.sum_linear(xs)[0] == m.sum_halves(xs)[0] == m.sum_loop(xs)[0] == 4


def test_recursion_limit(load):
    m = load("ex05_call_stack_space")
    assert m.hits_recursion_limit(m.sum_linear, 5000) is True
    assert m.hits_recursion_limit(m.sum_halves, 5000) is False
    assert m.hits_recursion_limit(m.sum_loop, 100_000) is False
