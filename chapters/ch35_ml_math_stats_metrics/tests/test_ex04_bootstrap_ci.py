import numpy as np
import pytest


def test_example(load):
    m = load("ex04_bootstrap_ci")
    lo, hi = m.bootstrap_ci(np.arange(10.0), np.mean, n_boot=500, seed=1)
    assert lo < 4.5 < hi


def test_vectorised_equals_loop(load):
    m = load("ex04_bootstrap_ci")
    x = np.random.default_rng(0).normal(size=25)
    for stat in (np.mean, np.median):
        assert m.bootstrap_ci(x, stat, n_boot=300, seed=4) == m.bootstrap_ci_loop(x, stat, n_boot=300, seed=4)


def test_percentile_definition_by_hand(load):
    m = load("ex04_bootstrap_ci")
    x = np.array([1.0, 2.0, 4.0, 8.0])
    rng = np.random.default_rng(9)
    idx = rng.integers(0, 4, size=(200, 4))
    stats = x[idx].mean(axis=1)
    expected = tuple(np.quantile(stats, [0.05, 0.95]).tolist())
    assert m.bootstrap_ci(x, np.mean, n_boot=200, alpha=0.1, seed=9) == pytest.approx(expected)


def test_normal_ci_by_hand(load):
    m = load("ex04_bootstrap_ci")
    x = np.array([1.0, 2.0, 3.0, 4.0])          # mean 2.5, s = sqrt(5/3) with ddof=1
    half = 1.959963984540054 * np.sqrt(5 / 3) / 2
    assert m.normal_ci_mean(x) == pytest.approx((2.5 - half, 2.5 + half))


def test_bootstrap_close_to_normal_for_large_n(load):
    m = load("ex04_bootstrap_ci")
    x = np.random.default_rng(5).normal(10, 2, size=2000)
    b, n = m.bootstrap_ci(x, np.mean, n_boot=2000, seed=1), m.normal_ci_mean(x)
    assert b == pytest.approx(n, abs=0.02)


def test_wider_interval_for_smaller_alpha(load):
    m = load("ex04_bootstrap_ci")
    x = np.random.default_rng(6).exponential(size=50)
    lo90, hi90 = m.bootstrap_ci(x, alpha=0.10, seed=2)
    lo99, hi99 = m.bootstrap_ci(x, alpha=0.01, seed=2)
    assert lo99 < lo90 < hi90 < hi99


def test_constant_and_invalid(load):
    m = load("ex04_bootstrap_ci")
    assert m.bootstrap_ci(np.full(6, 2.0)) == (2.0, 2.0)
    for bad in ([1.0], np.ones((3, 3))):
        with pytest.raises(ValueError):
            m.bootstrap_ci(bad)
    with pytest.raises(ValueError):
        m.bootstrap_ci([1.0, 2.0], alpha=1.5)


def test_coverage_near_nominal_for_large_n(load):
    m = load("ex04_bootstrap_ci")
    assert 0.90 <= m.coverage("bootstrap", 100, reps=200, n_boot=500) <= 0.99
