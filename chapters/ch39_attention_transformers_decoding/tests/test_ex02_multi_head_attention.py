import numpy as np
import pytest


def test_split_example_and_roundtrip(load):
    m = load("ex02_multi_head_attention")
    x = np.arange(8.0).reshape(1, 2, 4)
    assert m.split_heads(x, 2)[0].tolist() == [[[0.0, 1.0], [4.0, 5.0]], [[2.0, 3.0], [6.0, 7.0]]]
    y = np.random.default_rng(0).standard_normal((3, 5, 12))
    for H in (1, 2, 3, 4, 6, 12):
        s = m.split_heads(y, H)
        dh = 12 // H
        h = H - 1
        assert s.shape == (3, H, 5, dh)
        assert np.array_equal(s[:, h, 2], y[:, 2, h * dh:(h + 1) * dh])
        assert np.array_equal(m.merge_heads(s), y)


def test_indivisible_raises(load):
    m = load("ex02_multi_head_attention")
    with pytest.raises(ValueError):
        m.split_heads(np.zeros((1, 2, 8)), 3)
    with pytest.raises(ValueError):
        m.mha_loop(np.zeros((1, 2, 8)), m.init_params(8, np.random.default_rng(0)), 3)


@pytest.mark.parametrize("H", [1, 2, 4, 8])
def test_fused_equals_loop(load, H):
    m = load("ex02_multi_head_attention")
    rng = np.random.default_rng(H)
    x = rng.standard_normal((2, 6, 8))
    p = m.init_params(8, rng)
    mask = np.tril(np.ones((6, 6), bool))
    assert np.allclose(m.mha(x, p, H, mask), m.mha_loop(x, p, H, mask))
    assert np.allclose(m.mha(x, p, H), m.mha_loop(x, p, H))


def test_wrong_reshape_detected(load):
    m = load("ex02_multi_head_attention")
    rng = np.random.default_rng(5)
    x = rng.standard_normal((1, 4, 8))
    p = m.init_params(8, rng)
    assert not np.allclose(m.mha(x, p, 2), m.mha(x, p, 2, splitter=m.split_heads_wrong))


def test_param_count(load):
    m = load("ex02_multi_head_attention")
    assert m.mha_param_count(8) == 288 and m.mha_param_count(768) == 2362368


def test_against_torch(load):
    torch = pytest.importorskip("torch")
    m = load("ex02_multi_head_attention")
    rng = np.random.default_rng(9)
    D, H = 12, 3
    x = rng.standard_normal((2, 5, D))
    p = m.init_params(D, rng)
    ref = torch.nn.MultiheadAttention(D, H, batch_first=True, dtype=torch.float64)
    with torch.no_grad():
        ref.in_proj_weight.copy_(torch.from_numpy(np.concatenate([p["Wq"].T, p["Wk"].T, p["Wv"].T])))
        ref.in_proj_bias.copy_(torch.from_numpy(np.concatenate([p["bq"], p["bk"], p["bv"]])))
        ref.out_proj.weight.copy_(torch.from_numpy(p["Wo"].T))
        ref.out_proj.bias.copy_(torch.from_numpy(p["bo"]))
        xt = torch.from_numpy(x)
        out, _ = ref(xt, xt, xt, need_weights=False)
    assert np.allclose(out.numpy(), m.mha(x, p, H))
