import math

import numpy as np
import pytest


def test_param_count(load):
    m = load("ex06_transformer_block")
    assert m.block_param_count(768, 3072) == 12 * 768 ** 2 + 13 * 768 == 7087872
    p = m.init_block(8, 20, np.random.default_rng(0))
    assert sum(a.size for a in p.values()) == m.block_param_count(8, 20)


def test_gelu_values(load):
    m = load("ex06_transformer_block")
    assert m.gelu(np.array(0.0)) == 0.0
    assert math.isclose(float(m.gelu(np.array(1.0))), 0.8411919906, rel_tol=1e-8)
    assert math.isclose(float(m.gelu(np.array(-3.0))), -0.0036373920, rel_tol=1e-6)


def _setup(seed=1, B=2, T=5, D=8, F=32):
    rng = np.random.default_rng(seed)
    return rng.standard_normal((B, T, D)), rng


def test_pre_ln_structure(load):
    m = load("ex06_transformer_block")
    x, rng = _setup()
    p = m.init_block(8, 32, rng)
    causal = np.tril(np.ones((5, 5), bool))
    ln = lambda z, g, b: (z - z.mean(-1, keepdims=True)) / np.sqrt(z.var(-1, keepdims=True) + 1e-5) * g + b
    h = x + m.mha(ln(x, p["g1"], p["be1"]), p, 2, causal)
    expected = h + m.mlp(ln(h, p["g2"], p["be2"]), p)
    assert np.allclose(m.block(x, p, 2, causal, norm_first=True), expected)
    assert np.allclose(m.block_per_token(x, p, 2, causal), expected)


def test_post_ln_structure(load):
    m = load("ex06_transformer_block")
    x, rng = _setup(2)
    p = m.init_block(8, 32, rng)
    post = m.block(x, p, 4, None, norm_first=False)
    z = (post - p["be2"]) / p["g2"]
    assert np.allclose(z.mean(-1), 0, atol=1e-9) and np.allclose(z.var(-1), 1, atol=1e-3)
    assert not np.allclose(post, m.block(x, p, 4, None, norm_first=True))


def test_causal_block(load):
    m = load("ex06_transformer_block")
    x, rng = _setup(3)
    p = m.init_block(8, 32, rng)
    causal = np.tril(np.ones((5, 5), bool))
    x2 = x.copy()
    x2[:, 3:] += 1.0
    a, b = m.block(x, p, 2, causal), m.block(x2, p, 2, causal)
    assert np.allclose(a[:, :3], b[:, :3]) and not np.allclose(a[:, 3:], b[:, 3:])


@pytest.mark.parametrize("norm_first", [True, False])
def test_against_torch(load, norm_first):
    torch = pytest.importorskip("torch")
    m = load("ex06_transformer_block")
    x, rng = _setup(4, T=6, D=12)
    p = m.init_block(12, 24, rng)
    causal = np.tril(np.ones((6, 6), bool))
    layer = m.to_torch(p, 12, 3, 24, norm_first)
    with torch.no_grad():
        ref = layer(torch.from_numpy(x), src_mask=torch.from_numpy(~causal)).numpy()
    assert np.allclose(ref, m.block(x, p, 3, causal, norm_first=norm_first))
