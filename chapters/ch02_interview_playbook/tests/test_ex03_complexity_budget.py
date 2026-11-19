import pytest


@pytest.mark.parametrize("n, largest", [
    (1, "O(n!)"), (10, "O(n!)"), (20, "O(2^n)"), (500, "O(n^2)"),
    (3_000, "O(n^2)"), (10**5, "O(n log n)"), (10**6, "O(n)"), (10**9, "O(log n)"),
])
def test_feasible_largest(load, n, largest):
    m = load("ex03_complexity_budget")
    assert m.feasible(n)[-1] == largest


def test_feasible_is_prefix_of_classes(load):
    m = load("ex03_complexity_budget")
    for n in [2, 50, 10**4, 10**7, 10**12]:
        got = m.feasible(n)
        assert got == m.CLASSES[:len(got)]


def test_budget_parameters(load):
    m = load("ex03_complexity_budget")
    assert m.feasible(10**6, ops_per_second=10**8)[-1] == "O(n log n)"
    assert m.feasible(10**6, ops_per_second=10**8, seconds=0.001)[-1] == "O(log n)"


def test_huge_n_is_safe(load):
    m = load("ex03_complexity_budget")
    assert m.feasible(10**18)[-1] == "O(log n)"


def test_invalid_n(load):
    m = load("ex03_complexity_budget")
    with pytest.raises(ValueError):
        m.feasible(0)


def test_doubling(load):
    m = load("ex03_complexity_budget")
    assert m.doubling_exponent(m.ops_brute, 1000) == pytest.approx(2.0, abs=0.01)
    assert m.doubling_exponent(m.ops_hash, 1000) == pytest.approx(1.0, abs=0.01)
    assert m.doubling_exponent(lambda n: n ** 3 + 7, 100) == pytest.approx(3.0, abs=0.01)
    assert m.doubling_exponent(lambda n: 42, 100) == 0.0
