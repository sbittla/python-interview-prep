import numpy as np
import pytest


def test_example(load):
    m = load("ex08_pr_auc_calibration")
    assert m.average_precision([1, 0, 1, 0], [0.9, 0.8, 0.7, 0.1]) == pytest.approx(0.5 * 1 + 0.5 * 2 / 3)


def test_ties_by_hand(load):
    m = load("ex08_pr_auc_calibration")
    # thresholds 0.8: P=1/2 R=1/3; 0.5: P=2/3 R=2/3; 0.3: P=3/5 R=1
    expected = (1 / 3) * 0.5 + (1 / 3) * (2 / 3) + (1 / 3) * 0.6
    assert m.average_precision([1, 0, 1, 1, 0], [0.8, 0.8, 0.5, 0.3, 0.3]) == pytest.approx(expected)


@pytest.mark.parametrize("seed", range(5))
def test_fast_equals_brute_on_tied_data(load, seed):
    m = load("ex08_pr_auc_calibration")
    rng = np.random.default_rng(seed)
    y = (rng.random(200) < 0.3).astype(int)
    y[0] = 1
    p = rng.integers(0, 8, size=200) / 8
    assert m.average_precision(y, p) == pytest.approx(m.average_precision_brute(y, p), abs=1e-12)


def test_without_ties_equals_mean_precision_at_each_positive(load):
    m = load("ex08_pr_auc_calibration")
    rng = np.random.default_rng(1)
    y = (rng.random(100) < 0.2).astype(int)
    y[0] = 1
    s = rng.normal(size=100)
    order = np.argsort(-s)
    hits = np.cumsum(y[order])
    precisions = hits / np.arange(1, 101)
    assert m.average_precision(y, s) == pytest.approx(precisions[y[order] == 1].mean())


def test_trapezoid_differs_from_ap(load):
    m = load("ex08_pr_auc_calibration")
    y, p = [1, 0, 1, 0], [0.9, 0.8, 0.7, 0.1]
    assert m.pr_auc_trapezoid(y, p) == pytest.approx(0.5 * 1 + 0.5 * (0.5 + 2 / 3) / 2)
    assert m.pr_auc_trapezoid(y, p) != pytest.approx(m.average_precision(y, p))


def test_perfect_ranking_and_no_positives(load):
    m = load("ex08_pr_auc_calibration")
    assert m.average_precision([0, 1, 1], [0.1, 0.8, 0.9]) == 1.0
    with pytest.raises(ValueError):
        m.average_precision([0, 0], [0.3, 0.4])


def test_brier_and_ece_by_hand(load):
    m = load("ex08_pr_auc_calibration")
    assert m.brier([1, 0], [0.8, 0.4]) == pytest.approx((0.04 + 0.16) / 2)
    # bin 0: y=0, p=0.05 -> 0.05; bin 9: y sum 3, p sum 2.9 -> 0.1; ECE = 0.15 / 4
    assert m.ece([0, 1, 1, 1], [0.05, 0.95, 0.95, 1.0]) == pytest.approx(0.0375)
    assert m.ece([1, 0], [1.0, 0.0]) == 0.0


def test_overconfidence_hurts_ece_not_ap(load):
    m = load("ex08_pr_auc_calibration")
    rng = np.random.default_rng(4)
    q = rng.uniform(0.05, 0.95, 5000)
    y = (rng.random(5000) < q).astype(int)
    over = 1 / (1 + np.exp(-3 * np.log(q / (1 - q))))
    assert m.average_precision(y, over) == pytest.approx(m.average_precision(y, q))
    assert m.ece(y, over) > 5 * m.ece(y, q)
    assert m.brier(y, over) > m.brier(y, q)
