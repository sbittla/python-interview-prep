from math import sqrt

import pytest


def test_example(load):
    m = load("ex05_ab_test")
    z, p = m.two_proportion_ztest(200, 2000, 250, 2000)
    assert round(z, 3) == 2.502 and round(p, 4) == 0.0124


def test_hand_computed_z(load):
    m = load("ex05_ab_test")
    pooled = 90 / 300
    z_expected = (50 / 150 - 40 / 150) / sqrt(pooled * (1 - pooled) * (2 / 150))
    z, _ = m.two_proportion_ztest(40, 150, 50, 150)
    assert z == pytest.approx(z_expected)


def test_one_vs_two_sided(load):
    m = load("ex05_ab_test")
    _, p2 = m.two_proportion_ztest(200, 2000, 250, 2000)
    _, p1 = m.two_proportion_ztest(200, 2000, 250, 2000, "larger")
    assert p1 == pytest.approx(p2 / 2)
    _, p_other_way = m.two_proportion_ztest(250, 2000, 200, 2000, "larger")   # B is worse
    assert p_other_way == pytest.approx(1 - p1)


def test_symmetry_and_unequal_sizes(load):
    m = load("ex05_ab_test")
    z_ab, p_ab = m.two_proportion_ztest(30, 400, 55, 600)
    z_ba, p_ba = m.two_proportion_ztest(55, 600, 30, 400)
    assert z_ab == pytest.approx(-z_ba) and p_ab == pytest.approx(p_ba)


def test_no_difference_gives_p_one(load):
    z, p = load("ex05_ab_test").two_proportion_ztest(100, 1000, 100, 1000)
    assert z == 0 and p == pytest.approx(1.0)


def test_permutation_agrees_with_ztest(load):
    m = load("ex05_ab_test")
    _, p = m.two_proportion_ztest(60, 500, 85, 500)
    assert m.permutation_pvalue(60, 500, 85, 500, n_perm=4000, seed=1) == pytest.approx(p, abs=0.01)


def test_ci_contains_difference_and_excludes_zero(load):
    lo, hi = load("ex05_ab_test").diff_ci(200, 2000, 250, 2000)
    assert 0 < lo < 0.025 < hi


def test_sample_size_gives_target_power(load):
    m = load("ex05_ab_test")
    n = m.sample_size_per_arm(0.10, 0.12)
    assert 3700 < n < 4000
    assert m.simulated_power(0.10, 0.12, n, sims=20_000, seed=3) == pytest.approx(0.80, abs=0.02)
    assert m.sample_size_per_arm(0.10, 0.11) > 3 * n          # halving the effect ~ quadruples n


def test_peeking_inflates_false_positives(load):
    m = load("ex05_ab_test")
    once = m.peeking_false_positive_rate(looks=1, n_per_look=5000, sims=4000, seed=2)
    peek = m.peeking_false_positive_rate(looks=20, n_per_look=250, sims=4000, seed=2)
    assert 0.035 < once < 0.065
    assert peek > 0.15


def test_zero_se_and_bad_alternative_raise(load):
    m = load("ex05_ab_test")
    for args in [(0, 10, 0, 10), (10, 10, 10, 10)]:
        with pytest.raises(ValueError):
            m.two_proportion_ztest(*args)
    with pytest.raises(ValueError):
        m.two_proportion_ztest(1, 10, 2, 10, alternative="smaller")
