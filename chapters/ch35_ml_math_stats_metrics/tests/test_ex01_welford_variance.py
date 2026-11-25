import random
import statistics

import pytest


def test_examples(load):
    m = load("ex01_welford_variance")
    data = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    assert m.solve(data, ddof=0) == (5.0, 4.0)
    mean, var = m.solve(data, ddof=1)
    assert mean == 5.0 and var == pytest.approx(32 / 7, rel=1e-12)


def test_large_offset_is_accurate_but_naive_is_not(load):
    m = load("ex01_welford_variance")
    xs = [1e9 + v for v in (4.0, 7.0, 13.0, 16.0)]
    assert m.solve(xs)[1] == pytest.approx(30.0, rel=1e-9)
    assert m.two_pass_variance(xs) == pytest.approx(30.0, rel=1e-9)
    assert abs(m.naive_variance(xs) - 30.0) > 1.0      # the cancellation the exercise is about


def test_random_against_statistics_module(load):
    m = load("ex01_welford_variance")
    rng = random.Random(1)
    for _ in range(200):
        xs = [rng.uniform(-1e3, 1e3) for _ in range(rng.randint(2, 60))]
        mean, var = m.solve(xs, ddof=1)
        assert mean == pytest.approx(statistics.fmean(xs), rel=1e-12, abs=1e-9)
        assert var == pytest.approx(statistics.variance(xs), rel=1e-9)
        assert m.solve(xs, ddof=0)[1] == pytest.approx(statistics.pvariance(xs), rel=1e-9)


def test_merge_equals_single_pass(load):
    m = load("ex01_welford_variance")
    rng = random.Random(2)
    xs = [rng.gauss(5, 3) for _ in range(101)]
    for cut in (0, 1, 50, 101):
        a, b = m.RunningStats(), m.RunningStats()
        for x in xs[:cut]:
            a.push(x)
        for x in xs[cut:]:
            b.push(x)
        merged = a.merge(b)
        assert merged.n == 101
        assert merged.mean == pytest.approx(statistics.fmean(xs), rel=1e-12)
        assert merged.variance(1) == pytest.approx(statistics.variance(xs), rel=1e-9)


@pytest.mark.parametrize("xs, ddof", [([], 0), ([3.0], 1), ([1.0, 2.0], 2)])
def test_too_few_values_raise(load, xs, ddof):
    with pytest.raises(ValueError):
        load("ex01_welford_variance").solve(xs, ddof)


def test_constant_values_have_zero_variance(load):
    assert load("ex01_welford_variance").solve([7.5] * 10) == (7.5, 0.0)
