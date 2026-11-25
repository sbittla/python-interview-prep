import numpy as np
import pytest


def test_examples(load):
    m = load("ex09_regression_metrics")
    yt, yp = [3, -0.5, 2, 7], [2.5, 0.0, 2, 8]
    assert (m.mse(yt, yp), m.mae(yt, yp)) == (0.375, 0.5)
    assert m.rmse(yt, yp) == pytest.approx(np.sqrt(0.375))
    # SS_tot = 29.1875, SS_res = 1.5
    assert m.r2(yt, yp) == pytest.approx(1 - 1.5 / 29.1875)


def test_r2_reference_points(load):
    m = load("ex09_regression_metrics")
    y = [1.0, 2.0, 4.0, 9.0]
    assert m.r2(y, y) == 1.0
    assert m.r2(y, [np.mean(y)] * 4) == pytest.approx(0.0)
    assert m.r2([1, 2, 3], [3, 2, 1]) == pytest.approx(-3.0)


def test_r2_constant_target_convention(load):
    m = load("ex09_regression_metrics")
    assert m.r2([4, 4, 4], [4, 4, 4]) == 1.0
    assert m.r2([4, 4, 4], [4, 5, 4]) == 0.0


def test_mean_minimises_mse_median_minimises_mae(load):
    m = load("ex09_regression_metrics")
    y = [1.0, 2.0, 2.0, 3.0, 50.0]
    assert m.best_constant(y, "mse") == pytest.approx(np.mean(y), abs=0.01)
    assert m.best_constant(y, "mae") == pytest.approx(np.median(y), abs=0.01)


def test_outlier_moves_mse_more_than_mae(load):
    m = load("ex09_regression_metrics")
    base_t, base_p = [1, 2, 3, 4], [1.5, 2.5, 3.5, 4.5]
    out_p = [1.5, 2.5, 3.5, 14.5]
    assert m.mse(base_t, out_p) / m.mse(base_t, base_p) > m.mae(base_t, out_p) / m.mae(base_t, base_p)


def test_mape(load):
    m = load("ex09_regression_metrics")
    assert m.mape([100, 200], [110, 180]) == pytest.approx(0.1)
    with pytest.raises(ValueError):
        m.mape([0, 1], [1, 1])


@pytest.mark.parametrize("fn", ["mse", "rmse", "mae", "r2"])
@pytest.mark.parametrize("a, b", [([], []), ([1, 2], [1])])
def test_invalid_inputs(load, fn, a, b):
    with pytest.raises(ValueError):
        getattr(load("ex09_regression_metrics"), fn)(a, b)
