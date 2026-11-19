import pytest


@pytest.mark.parametrize("text, expected", [
    ("1 <= nums.length <= 2 * 10^5", 200_000),
    ("1 <= n <= 10**4", 10_000),
    ("0 <= k <= 1e9", 1_000_000_000),
    ("n <= 5,000", 5_000),
    ("1 <= n <= 8", 8),
    ("-10^4 <= nums[i] <= 10^4", 10_000),
    ("1 <= m, n <= 300 and 1 <= q <= 2.5e4", 25_000),
])
def test_parse_bound(load, text, expected):
    assert load("ex02_constraint_advisor").parse_bound(text) == expected


def test_parse_bound_no_number(load):
    with pytest.raises(ValueError):
        load("ex02_constraint_advisor").parse_bound("n is small")


@pytest.mark.parametrize("n, expected", [
    (1, "O(n!)"), (10, "O(n!)"), (11, "O(2^n)"), (20, "O(2^n)"), (21, "O(n^3)"),
    (500, "O(n^3)"), (501, "O(n^2)"), (5_000, "O(n^2)"), (5_001, "O(n log n)"),
    (10**6, "O(n log n)"), (10**6 + 1, "O(n)"), (10**8, "O(n)"), (10**8 + 1, "O(log n)"),
])
def test_max_complexity_boundaries(load, n, expected):
    assert load("ex02_constraint_advisor").max_complexity(n) == expected


def test_max_complexity_rejects_zero(load):
    with pytest.raises(ValueError):
        load("ex02_constraint_advisor").max_complexity(0)


def test_estimated_ops(load):
    m = load("ex02_constraint_advisor")
    assert m.estimated_ops("O(n log n)", 1024) == 10 * 1024
    assert m.estimated_ops("O(n^2)", 5000) == 25_000_000
    assert m.estimated_ops("O(2^n)", 20) == 20 * 2**20
    assert m.estimated_ops("O(n!)", 10) == 3_628_800
    assert m.estimated_ops("O(log n)", 10**18) == 60   # must not build huge numbers
    assert m.estimated_ops("O(1)", 1) == 1


@pytest.mark.parametrize("n, budget, expected", [
    (10, 10**8, "O(n!)"), (500, 10**8, "O(n^2)"), (10**5, 10**8, "O(n log n)"),
    (10**7, 10**8, "O(n)"), (10**12, 10**8, "O(log n)"), (20, 10**7, "O(n^3)"),
])
def test_slowest_feasible(load, n, budget, expected):
    assert load("ex02_constraint_advisor").slowest_feasible(n, budget) == expected


@pytest.mark.parametrize("n, expected", [
    (10, "O(n!)"), (11, "O(2^n)"), (18, "O(2^n)"), (19, "O(n^3)"), (200, "O(n^3)"),
    (201, "O(n^2)"), (3_000, "O(n^2)"), (3_001, "O(n log n)"), (5 * 10**5, "O(n log n)"),
    (5 * 10**5 + 1, "O(n)"), (10**7, "O(n)"), (10**7 + 1, "O(log n)"),
])
def test_max_complexity_cpython_column(load, n, expected):
    assert load("ex02_constraint_advisor").max_complexity(n, python=True) == expected


@pytest.mark.parametrize("label, expected", [
    ("O(n!)", 10), ("O(2^n)", 19), ("O(n^3)", 215), ("O(n^2)", 3162), ("O(n)", 10**7),
])
def test_max_n(load, label, expected):
    assert load("ex02_constraint_advisor").max_n(label, 10**7) == expected


def test_cpython_column_fits_its_budget(load):
    m = load("ex02_constraint_advisor")
    for _, cpython, label, _ in m.TABLE[:-1]:
        assert estimated_ops_ok(m, label, int(cpython))


def estimated_ops_ok(m, label, n):
    return m.estimated_ops(label, n) <= m.PYTHON_STEPS
