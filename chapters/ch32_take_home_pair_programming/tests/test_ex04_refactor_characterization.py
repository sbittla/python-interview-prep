import pytest

M = "ex04_refactor_characterization"


def test_grid_shape(load):
    m = load(M)
    grid = m.default_grid()
    assert len(grid) == 208 and len(set(grid)) == 208
    assert (0, "mars", True, False) in grid


def test_record_captures_exceptions(load):
    m = load(M)

    def f(x):
        return 10 // x

    assert m.record(f, [(2,), (0,)]) == {(2,): 5, (0,): "raises ZeroDivisionError"}


def test_compare_reports_in_case_order(load):
    m = load(M)
    diffs = m.compare(lambda x: x, lambda x: abs(x), [(1,), (-2,), (0,), (-1,)])
    assert diffs == [((-2,), -2, 2), ((-1,), -1, 1)]


def test_clean_matches_legacy_everywhere(load):
    m = load(M)
    assert m.compare(m.shipping_cost_legacy, m.shipping_cost, m.default_grid()) == []


@pytest.mark.parametrize("case, expected", [
    ((0, "eu", True, True), 0),
    ((1, "domestic", False, False), 500),
    ((1001, "domestic", True, False), 1700),
    ((10000, "eu", False, False), 4050),
    ((10001, "eu", False, False), 5400),
    ((1000, "intl", False, True), 2000),        # exactly 2000: no member discount
    ((1001, "mars", False, True), 2000),        # 2500 - 500; unknown zone = intl
    ((2000, "intl", True, False), 3750),
    ((1500, "eu", False, False), 1250),         # off-grid weight
])
def test_known_values(load, case, expected):
    m = load(M)
    assert m.shipping_cost_legacy(*case) == expected
    assert m.shipping_cost(*case) == expected


def test_tempting_refactor_is_caught(load):
    m = load(M)
    diffs = m.compare(m.shipping_cost_legacy, m.shipping_cost_tempting, m.default_grid())
    assert len(diffs) == 38                     # 32 non-positive weights + 6 cost==2000 cases
    assert ((1000, "intl", False, True), 2000, 1500) in diffs
    assert ((0, "eu", False, False), 0, "raises ValueError") in diffs


def test_weak_grid_hides_the_boundary_bug(load):
    m = load(M)
    weak = [c for c in m.default_grid() if c[0] not in (-1, 0, 1, 999, 1000)]
    assert m.compare(m.shipping_cost_legacy, m.shipping_cost_tempting, weak) == []
