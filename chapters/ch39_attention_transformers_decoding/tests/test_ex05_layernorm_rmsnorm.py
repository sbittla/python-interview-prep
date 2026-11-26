import numpy as np
import pytest


def test_examples(load):
    m = load("ex05_layernorm_rmsnorm")
    got = m.layer_norm(np.array([1.0, 2.0, 3.0]), np.ones(3), np.zeros(3))
    assert np.allclose(got, np.array([-1.0, 0.0, 1.0]) / np.sqrt(2 / 3 + 1e-5))
    assert np.allclose(m.rms_norm(np.array([3.0, 4.0]), np.ones(2), eps=0.0), np.array([3, 4]) / np.sqrt(12.5))


def test_against_reference(load):
    m = load("ex05_layernorm_rmsnorm")
    rng = np.random.default_rng(0)
    x = rng.standard_normal((3, 4, 7)) * 4 + 2
    g, b = rng.standard_normal(7), rng.standard_normal(7)
    mu, var = x.mean(-1, keepdims=True), x.var(-1, keepdims=True)
    assert np.allclose(m.layer_norm(x, g, b), (x - mu) / np.sqrt(var + 1e-5) * g + b)
    assert np.allclose(m.layer_norm(x, g, b), m.layer_norm_loop(x, g, b))
    assert np.allclose(m.rms_norm(x, g), x / np.sqrt((x ** 2).mean(-1, keepdims=True) + 1e-6) * g)


def test_eps_inside_sqrt(load):
    m = load("ex05_layernorm_rmsnorm")
    x = np.array([0.0, 1e-3])                 # var = 2.5e-7, comparable with eps
    got = m.layer_norm(x, np.ones(2), np.zeros(2), eps=1e-6)
    assert np.allclose(got, (x - 5e-4) / np.sqrt(2.5e-7 + 1e-6))
    small = np.array([1e-3, -1e-3])           # mean square 1e-6, equal to eps
    assert np.allclose(m.rms_norm(small, np.ones(2), eps=1e-6), small / np.sqrt(2e-6))


def test_invariances_and_degenerate(load):
    m = load("ex05_layernorm_rmsnorm")
    rng = np.random.default_rng(1)
    x, g, b = rng.standard_normal((5, 6)), rng.standard_normal(6), rng.standard_normal(6)
    assert np.allclose(m.layer_norm(3 * x + 7, g, b, eps=1e-12), m.layer_norm(x, g, b, eps=1e-12))
    assert np.allclose(m.rms_norm(3 * x, g, eps=1e-12), m.rms_norm(x, g, eps=1e-12))
    assert not np.allclose(m.rms_norm(x + 7, g), m.rms_norm(x, g), atol=1e-3)
    assert np.allclose(m.layer_norm(np.full(6, 4.0), g, b), b)
    assert np.allclose(m.rms_norm(np.zeros(6), g), 0)
    assert m.norm_params(10, "layernorm") == 20 and m.norm_params(10, "rmsnorm") == 10


def test_against_torch(load):
    torch = pytest.importorskip("torch")
    F = torch.nn.functional
    m = load("ex05_layernorm_rmsnorm")
    rng = np.random.default_rng(2)
    x, g, b = rng.standard_normal((2, 3, 5)), rng.standard_normal(5), rng.standard_normal(5)
    t = torch.from_numpy
    assert np.allclose(F.layer_norm(t(x), (5,), t(g), t(b), eps=1e-5).numpy(), m.layer_norm(x, g, b))
    assert np.allclose(F.rms_norm(t(x), (5,), t(g), eps=1e-6).numpy(), m.rms_norm(x, g))
