import pytest


def test_examples(load):
    m = load("ex09_generate_parentheses")
    assert m.solve(1) == ["()"]
    assert m.solve(3) == ["((()))", "(()())", "(())()", "()(())", "()()()"]


@pytest.mark.parametrize("n, catalan", [(2, 2), (4, 14), (5, 42), (8, 1430)])
def test_catalan_counts(load, n, catalan):
    m = load("ex09_generate_parentheses")
    assert len(m.solve(n)) == catalan


def test_matches_brute_force(load):
    m = load("ex09_generate_parentheses")
    assert m.solve(5) == m.brute_force(5)
