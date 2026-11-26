import numpy as np
import pytest


@pytest.fixture
def setup(load):
    m = load("ex08_kv_cache")
    params = m.init_model(V=17, T_max=20, D=12, H=3, L=2, rng=np.random.default_rng(0))
    return m, params


def test_greedy_identical(setup):
    m, params = setup
    prompt = np.random.default_rng(1).integers(0, 17, (3, 4))
    a = m.generate_greedy(params, prompt, 12, use_cache=False)
    b = m.generate_greedy(params, prompt, 12, use_cache=True)
    assert a.shape == (3, 16) and np.array_equal(a, b)


@pytest.mark.parametrize("chunks", [[6], [1, 1, 1, 1, 1, 1], [2, 3, 1], [4, 2]])
def test_logits_match_full_recompute(setup, chunks):
    m, params = setup
    tokens = np.random.default_rng(2).integers(0, 17, (2, 6))
    cache = m.new_cache(params, 2)
    outs, start = [], 0
    for n in chunks:
        outs.append(m.extend(params, tokens[:, start:start + n], cache))
        start += n
    assert cache.length == 6
    assert np.abs(np.concatenate(outs, 1) - m.full_forward(params, tokens)).max() < 1e-10


def test_cache_layout_and_contents(setup):
    m, params = setup
    cache = m.new_cache(params, 2)
    assert cache.k.shape == cache.v.shape == (2, 2, 3, 20, 4)
    tokens = np.random.default_rng(3).integers(0, 17, (2, 5))
    m.extend(params, tokens, cache)
    assert np.any(cache.k[:, :, :, :5] != 0) and np.all(cache.k[:, :, :, 5:] == 0)
    # layer-0 keys are LN(x) @ Wk for the embedded tokens
    x = params["E"][tokens] + params["P"][:5]
    h = (x - x.mean(-1, keepdims=True)) / np.sqrt(x.var(-1, keepdims=True) + 1e-5)
    k0 = (h @ params["blocks"][0]["Wk"]).reshape(2, 5, 3, 4).transpose(0, 2, 1, 3)
    assert np.allclose(cache.k[0, :, :, :5], k0)


def test_concat_rung_matches(setup):
    m, params = setup
    tokens = np.random.default_rng(4).integers(0, 17, (1, 7))
    kv = []
    outs = [m.extend_concat(params, tokens[:, :3], kv)]
    outs += [m.extend_concat(params, tokens[:, t:t + 1], kv) for t in range(3, 7)]
    assert np.allclose(np.concatenate(outs, 1), m.full_forward(params, tokens), atol=1e-10)


def test_position_bug_is_detected(setup):
    m, params = setup
    tokens = np.random.default_rng(5).integers(0, 17, (1, 5))
    cache = m.new_cache(params, 1)
    m.extend(params, tokens[:, :4], cache)
    wrong = m.extend(params, tokens[:, 4:], cache, position_bug=True)
    assert not np.allclose(wrong[:, 0], m.full_forward(params, tokens)[:, -1])


def test_errors(setup):
    m, params = setup
    cache = m.new_cache(params, 1)
    with pytest.raises(ValueError):
        m.extend(params, np.zeros((1, 0), int), cache)
    m.extend(params, np.zeros((1, 20), int), cache)
    with pytest.raises(ValueError):
        m.extend(params, np.zeros((1, 1), int), cache)


def test_kv_bytes(load):
    m = load("ex08_kv_cache")
    assert m.kv_cache_bytes(32, 1, 4096, 32, 128, 2) == 2 * 2**30
    assert m.kv_cache_bytes(32, 1, 4096, 8, 128, 2) == 2**29
    assert m.kv_cache_bytes(2, 3, 5, 7, 11, 4) == 2 * 2 * 3 * 5 * 7 * 11 * 4
