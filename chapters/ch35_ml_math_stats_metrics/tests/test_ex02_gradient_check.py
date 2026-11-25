import numpy as np
import pytest


def test_example_mse_grad(load):
    m = load("ex02_gradient_check")
    X = np.array([[1.0, 2.0], [3.0, 4.0]])
    y = np.array([1.0, 0.0])
    assert m.mse_grad(np.zeros(2), X, y).tolist() == [-0.5, -1.0]


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_analytic_gradients_pass_the_check(load, seed):
    m = load("ex02_gradient_check")
    rng = np.random.default_rng(seed)
    X, w = rng.normal(size=(30, 5)), rng.normal(size=5)
    y_reg, y_cls = rng.normal(size=30), (rng.random(30) < 0.5).astype(float)
    assert m.check_gradient(lambda v: m.mse_loss(v, X, y_reg), lambda v: m.mse_grad(v, X, y_reg), w) < 1e-7
    assert m.check_gradient(lambda v: m.logistic_loss(v, X, y_cls), lambda v: m.logistic_grad(v, X, y_cls), w) < 1e-7


def test_check_catches_wrong_gradient(load):
    m = load("ex02_gradient_check")
    rng = np.random.default_rng(3)
    X, y, w = rng.normal(size=(20, 3)), rng.normal(size=20), rng.normal(size=3)
    wrong = lambda v: 2 * m.mse_grad(v, X, y)                 # off by a factor of two
    assert m.check_gradient(lambda v: m.mse_loss(v, X, y), wrong, w) > 0.1


def test_numerical_grad_on_quadratic(load):
    m = load("ex02_gradient_check")
    A = np.array([[3.0, 1.0], [1.0, 2.0]])
    f = lambda v: float(v @ A @ v)                            # grad = 2 A v
    v = np.array([0.7, -1.3])
    assert np.allclose(m.numerical_grad(f, v), 2 * A @ v, atol=1e-8)
    assert np.allclose(m.numerical_grad(f, v, method="forward"), 2 * A @ v, atol=1e-4)


def test_central_more_accurate_than_forward(load):
    m = load("ex02_gradient_check")
    f = lambda v: float(np.exp(v[0]))
    x = np.array([1.0])
    fwd = abs(m.numerical_grad(f, x, 1e-4, "forward")[0] - np.e)
    cen = abs(m.numerical_grad(f, x, 1e-4, "central")[0] - np.e)
    assert cen < fwd / 100


def test_logistic_loss_is_finite_for_huge_logits(load):
    m = load("ex02_gradient_check")
    X = np.array([[1000.0], [-1000.0]])
    y = np.array([0.0, 1.0])
    loss = m.logistic_loss(np.array([1.0]), X, y)
    assert np.isfinite(loss) and loss == pytest.approx(1000.0)
    assert np.all(np.isfinite(m.logistic_grad(np.array([1.0]), X, y)))


def test_relative_error_and_bad_method(load):
    m = load("ex02_gradient_check")
    assert m.relative_error(np.zeros(3), np.zeros(3)) == 0.0
    assert m.relative_error(np.array([1.0]), np.array([-1.0])) == 1.0
    with pytest.raises(ValueError):
        m.numerical_grad(lambda v: 0.0, np.zeros(1), method="backward")
