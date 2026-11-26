import math

import numpy as np
import pytest


@pytest.fixture
def model(load):
    m = load("ex07_mini_gpt_forward")
    params = m.init_gpt(V=23, T_max=12, D=16, H=4, L=2, rng=np.random.default_rng(0))
    return m, params


def test_shapes_and_formula(model):
    m, params = model
    tokens = np.random.default_rng(1).integers(0, 23, (3, 7))
    assert m.forward(params, tokens).shape == (3, 7, 23)
    assert m.count_params(params) == m.gpt_param_formula(23, 12, 16, 2)
    assert m.gpt_param_formula(50257, 1024, 768, 12) == 124439808


def test_one_pass_equals_prefix_loop(model):
    m, params = model
    tokens = np.random.default_rng(2).integers(0, 23, (2, 9))
    assert np.allclose(m.forward(params, tokens), m.forward_prefix_loop(params, tokens))


def test_causal(model):
    m, params = model
    tokens = np.random.default_rng(3).integers(0, 23, (1, 8))
    base = m.forward(params, tokens)
    for t in range(1, 8):
        changed = tokens.copy()
        changed[0, t] = (changed[0, t] + 1) % 23
        new = m.forward(params, changed)
        assert np.allclose(new[:, :t], base[:, :t]) and not np.allclose(new[:, t], base[:, t])


def test_tied_head_and_positions(model):
    m, params = model
    tokens = np.array([[4, 4, 4]])
    logits = m.forward(params, tokens)
    assert not np.allclose(logits[0, 0], logits[0, 1])         # positions matter
    p2 = {**params, "E": params["E"] * 2}
    assert not np.allclose(m.forward(p2, tokens), logits)        # head uses E


def test_loss_near_ln_v_and_matches_manual(model):
    m, params = model
    tokens = np.random.default_rng(4).integers(0, 23, (2, 10))
    loss = m.next_token_loss(params, tokens)
    z = m.forward(params, tokens)[:, :-1]
    p = np.exp(z - z.max(-1, keepdims=True))
    p /= p.sum(-1, keepdims=True)
    manual = -np.mean(np.log(np.take_along_axis(p, tokens[:, 1:, None], -1)))
    assert math.isclose(loss, manual, rel_tol=1e-9)
    assert abs(loss - math.log(23)) < 0.2


def test_too_long_raises(model):
    m, params = model
    m.forward(params, np.zeros((1, 12), int))
    with pytest.raises(ValueError):
        m.forward(params, np.zeros((1, 13), int))


def test_final_layer_norm_and_tied_head_by_hand(load):
    m = load("ex07_mini_gpt_forward")
    rng = np.random.default_rng(6)
    params = m.init_gpt(V=11, T_max=5, D=8, H=2, L=0, rng=rng)       # no blocks: embed -> LN -> head
    params["gf"], params["bf"] = 1 + rng.standard_normal(8), rng.standard_normal(8)
    tokens = np.array([[3, 1, 4, 1]])
    x = params["E"][tokens] + params["P"][:4]
    h = (x - x.mean(-1, keepdims=True)) / np.sqrt(x.var(-1, keepdims=True) + 1e-5) * params["gf"] + params["bf"]
    assert np.allclose(m.forward(params, tokens), h @ params["E"].T)
