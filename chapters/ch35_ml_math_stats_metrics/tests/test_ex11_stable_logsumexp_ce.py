import math

import numpy as np
import pytest


def test_examples(load):
    m = load("ex11_stable_logsumexp_ce")
    assert float(m.logsumexp(np.array([1000.0, 1000.0]))) == pytest.approx(1000 + math.log(2))
    expected = math.log(math.exp(2) + math.exp(1) + math.exp(0.1)) - 2
    assert m.cross_entropy(np.array([[2.0, 1.0, 0.1]]), np.array([0])) == pytest.approx(expected)
    assert round(expected, 6) == 0.41703


def test_matches_naive_on_moderate_values(load):
    m = load("ex11_stable_logsumexp_ce")
    rng = np.random.default_rng(0)
    Z = rng.normal(scale=3, size=(8, 5))
    y = rng.integers(0, 5, size=8)
    assert np.allclose(m.logsumexp(Z), m.logsumexp_naive(Z))
    assert m.cross_entropy(Z, y) == pytest.approx(m.cross_entropy_naive(Z, y))
    assert np.allclose(m.softmax(Z).sum(axis=1), 1.0)


def test_shift_invariance_and_extremes(load):
    m = load("ex11_stable_logsumexp_ce")
    z = np.array([1.0, 2.0, 3.0])
    assert np.allclose(m.softmax(z + 1e4), m.softmax(z))
    assert m.cross_entropy(np.array([[800.0, 0.0]]), np.array([1])) == pytest.approx(800.0)
    assert m.log_softmax(np.array([0.0, -800.0])).tolist() == [0.0, -800.0]


def test_infinities(load):
    m = load("ex11_stable_logsumexp_ce")
    assert m.logsumexp(np.array([-np.inf, -np.inf])) == -np.inf
    assert m.logsumexp(np.array([-np.inf, 0.0])) == 0.0
    assert m.logsumexp(np.array([np.inf, 0.0])) == np.inf


def test_axis_argument(load):
    m = load("ex11_stable_logsumexp_ce")
    Z = np.array([[0.0, 1000.0], [3.0, -2.0]])
    col = m.logsumexp(Z, axis=0)
    assert col.shape == (2,)
    assert col[1] == pytest.approx(1000.0)
    assert np.allclose(m.softmax(Z, axis=0).sum(axis=0), 1.0)


def test_gradient_against_finite_differences(load):
    m = load("ex11_stable_logsumexp_ce")
    rng = np.random.default_rng(2)
    Z, y = rng.normal(size=(4, 3)), np.array([0, 2, 1, 2])
    num = np.zeros_like(Z)
    for idx in np.ndindex(Z.shape):
        e = np.zeros_like(Z)
        e[idx] = 1e-6
        num[idx] = (m.cross_entropy(Z + e, y) - m.cross_entropy(Z - e, y)) / 2e-6
    assert np.allclose(num, m.cross_entropy_grad(Z, y), atol=1e-8)
    assert np.allclose(m.cross_entropy_grad(Z, y).sum(axis=1), 0.0)   # rows of softmax - onehot sum to 0


def test_binary_losses(load):
    m = load("ex11_stable_logsumexp_ce")
    z = np.array([0.3, -1.2, 2.0])
    y = np.array([1.0, 0.0, 0.0])
    p = 1 / (1 + np.exp(-z))
    assert m.binary_log_loss_from_logits(z, y) == pytest.approx(m.binary_log_loss_from_probs(p, y))
    assert m.binary_log_loss_from_logits(np.array([0.0]), np.array([1.0])) == pytest.approx(math.log(2))
    big = m.binary_log_loss_from_logits(np.array([1000.0]), np.array([0.0]))
    assert big == pytest.approx(1000.0)
    assert m.binary_log_loss_from_probs(np.array([1.0]), np.array([0.0])) == pytest.approx(-math.log(1e-15), rel=0.1)


def test_single_class_loss_is_zero(load):
    m = load("ex11_stable_logsumexp_ce")
    assert m.cross_entropy(np.array([[5.0], [-3.0]]), np.array([0, 0])) == 0.0
