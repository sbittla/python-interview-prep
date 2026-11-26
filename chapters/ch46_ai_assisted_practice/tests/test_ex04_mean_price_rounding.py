import builtins
import math
import random
from fractions import Fraction

import pytest

M = "ex04_mean_price_rounding"


def ref(prices):
    if not prices:
        return None
    mean = sum(Fraction(p) for p in prices) / len(prices)
    cents = math.floor(mean * 100 + Fraction(1, 2))
    return f"{cents // 100}.{cents % 100:02d}"


def test_outcome_captures_exceptions(load):
    m = load(M)
    assert m.outcome(len, ["a"]) == 1
    assert m.outcome(lambda p: 1 / len(p), []) == "raises ZeroDivisionError"


def test_edge_cases_follow_the_spec_and_cover_the_traps(load):
    m = load(M)
    for prices, want in m.EDGE_CASES:
        assert want == ref(prices)
    assert ([], None) in m.EDGE_CASES
    assert len(m.EDGE_CASES) >= 4


def test_generated_fails_each_kind_of_trap(load):
    m = load(M)
    bad = m.failures(m.generated_mean_price, m.EDGE_CASES)
    outcomes = [got for _, _, got in bad]
    assert "raises ZeroDivisionError" in outcomes                      # empty input
    assert len(bad) >= 3                                               # plus rounding cases


def test_failures_reports_in_order(load):
    m = load(M)
    cases = [(["1"], "1.00"), (["2"], "9.99"), ([], None), (["3"], "0.00")]
    assert m.failures(m.mean_price, cases) == [(["2"], "9.99", "2.00"),
                                               (["3"], "0.00", "3.00")]


def test_fix_passes_edge_cases(load):
    m = load(M)
    assert len(m.EDGE_CASES) >= 4
    assert m.failures(m.mean_price, m.EDGE_CASES) == []


def test_oracle_and_fix_agree_with_reference_on_random_prices(load):
    m = load(M)
    rng = random.Random(2024)
    generated_wrong = 0
    for _ in range(3000):
        prices = [f"{rng.randint(0, 9999) / 1000:.3f}" for _ in range(rng.randint(1, 6))]
        assert m.oracle(prices) == ref(prices)
        assert m.mean_price(prices) == ref(prices)
        generated_wrong += m.generated_mean_price(prices) != ref(prices)
    assert generated_wrong > 0                                         # the bug is real


@pytest.mark.parametrize("prices, expected", [
    ([], None), (["0.125"], "0.13"), (["0.124"], "0.12"), (["1.005"], "1.01"),
    (["0"], "0.00"), (["0.005", "0.005"], "0.01"), (["10", "20", "20"], "16.67"),
    (["99999999.995"], "100000000.00"),
])
def test_fix_values(load, prices, expected):
    assert load(M).mean_price(prices) == expected


def test_fix_never_uses_float(load, monkeypatch):
    m = load(M)

    def no_float(*args):
        raise AssertionError("float() called")

    monkeypatch.setattr(builtins, "float", no_float)
    assert m.mean_price(["2.675", "1.005"]) == "1.84"


def test_complexity_stated(load):
    assert load(M).COMPLEXITY["time"].replace(" ", "").lower() == "o(n)"
