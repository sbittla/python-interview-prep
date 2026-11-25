import pytest

M = "ex04_refactor_characterization"


def kg(grams):
    return -(-grams // 1000)


def test_grid_covers_the_boundaries(load):
    m = load(M)
    grid = m.default_grid()
    weights = {g for g, _, _, _ in grid}
    zones = {z for _, z, _, _ in grid}
    assert len(grid) == len(set(grid)) == len(weights) * len(zones) * 4   # full product
    assert any(g <= 0 for g in weights)                    # the "return 0" branch
    assert any(kg(g) == 1 for g in weights if g > 0)       # first kg (member cost == 2000)
    assert any(kg(g) == 10 for g in weights)               # 10 kg ...
    assert any(kg(g) == 11 for g in weights)               # ... and just over (eu surcharge)
    assert {"domestic", "eu", "intl"} < zones              # plus at least one unknown zone
    assert {(e, mem) for _, _, e, mem in grid} == {(False, False), (False, True),
                                                    (True, False), (True, True)}


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
    dense = [(g, z, e, mem) for g in [-5, 0, *range(1, 30001, 499), 10000, 10001]
             for z in ("domestic", "eu", "intl", "moon") for e in (False, True)
             for mem in (False, True)]                     # independent of your grid
    assert m.compare(m.shipping_cost_legacy, m.shipping_cost, dense) == []


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
    assert any(c[0] <= 0 and old == 0 and new == "raises ValueError" for c, old, new in diffs)
    assert any(kg(c[0]) == 1 and c[1] != "domestic" and c[1] != "eu" and c[3]
               and (old, new) == (2000, 1500) for c, old, new in diffs)   # cost exactly 2000
    assert all(c[0] <= 0 or (old, new) == (2000, 1500) for c, old, new in diffs)


def test_weak_grid_hides_the_boundary_bug(load):
    m = load(M)
    weak = [c for c in m.default_grid() if c[0] > 1000]   # no 0 g, no 1-kg weights
    assert weak
    assert m.compare(m.shipping_cost_legacy, m.shipping_cost_tempting, weak) == []
