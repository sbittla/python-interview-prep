import pytest


def test_examples(load):
    m = load("ex01_op_counter")
    assert m.fit_growth({64: 64, 128: 128, 256: 256}) == "O(n)"
    assert m.growth_ratios({64: 4096, 128: 16384, 256: 65536}) == [4.0, 4.0]
    assert m.fit_growth({64: 6, 128: 7, 256: 8, 512: 9}) == "O(log n)"


@pytest.mark.parametrize("fn, sizes, expected", [
    ("constant_work", (64, 256, 1024), "O(1)"),
    ("halving", (64, 256, 1024), "O(log n)"),
    ("linear_scan", (64, 256, 1024), "O(n)"),
    ("merge_sort_count", (64, 256, 1024), "O(n log n)"),
    ("all_pairs", (32, 128, 512), "O(n^2)"),
    ("all_triples", (16, 32, 64), "O(n^3)"),
    ("subsets_count", (6, 9, 12), "O(2^n)"),
    ("permutations_count", (4, 5, 6, 7), "O(n!)"),
])
def test_instrumented_algorithms(load, fn, sizes, expected):
    m = load("ex01_op_counter")
    f = getattr(m, fn)
    assert m.fit_growth({n: f(n) for n in sizes}) == expected


def test_exact_counts(load):
    m = load("ex01_op_counter")
    assert m.halving(1024) == 10 and m.halving(1) == 0
    assert m.all_pairs(10) == 45
    assert m.subsets_count(5) == 32
    assert m.permutations_count(5) == 120
    assert m.merge_sort_count(8) == 24          # n * log2(n) element moves


@pytest.mark.parametrize("make, expected", [
    (lambda n: 7 * n * n + 100 * n, "O(n^2)"),     # lower-order term must not fool the fit
    (lambda n: 2 ** n * 3, "O(2^n)"),
    (lambda n: 5, "O(1)"),
    (lambda n: n ** 3 // 6, "O(n^3)"),
])
def test_synthetic_curves(load, make, expected):
    m = load("ex01_op_counter")
    sizes = (8, 10, 12, 14) if expected == "O(2^n)" else (64, 256, 1024, 4096)
    assert m.fit_growth({n: make(n) for n in sizes}) == expected


def test_order_of_points_does_not_matter(load):
    m = load("ex01_op_counter")
    assert m.growth_ratios({256: 8, 64: 2, 128: 4}) == [2.0, 2.0]


@pytest.mark.parametrize("bad", [{}, {8: 3}, {1: 1, 4: 4}, {4: 0, 8: 1}])
def test_invalid_input(load, bad):
    m = load("ex01_op_counter")
    with pytest.raises(ValueError):
        m.fit_growth(bad)
