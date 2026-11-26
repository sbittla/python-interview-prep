import math

import numpy as np
import pytest


def test_example(load):
    m = load("ex01_scaled_dot_product_attention")
    out, w = m.attention(np.eye(2), np.eye(2), np.eye(2), mask=np.array([[True, False], [True, True]]))
    a = 1 / (1 + math.exp(1 / math.sqrt(2)))
    assert np.allclose(w, [[1, 0], [a, 1 - a]])
    assert np.allclose(out, w)


def test_scaling_by_sqrt_dk(load):
    m = load("ex01_scaled_dot_product_attention")
    q = np.array([[1.0, 1.0, 1.0, 1.0]])
    k = np.array([[1.0, 1.0, 1.0, 1.0], [0.0, 0.0, 0.0, 0.0]])
    _, w = m.attention(q, k, np.eye(2))
    e = math.exp(4 / 2)                      # q.k = 4, sqrt(d_k) = 2
    assert np.allclose(w, [[e / (e + 1), 1 / (e + 1)]])


@pytest.mark.parametrize("seed", range(5))
def test_matches_loop_and_reference_with_mask(load, seed):
    m = load("ex01_scaled_dot_product_attention")
    rng = np.random.default_rng(seed)
    n, k, d = (int(v) for v in rng.integers(1, 6, 3))
    Q, K, V = rng.standard_normal((n, d)), rng.standard_normal((k, d)), rng.standard_normal((k, 3))
    mask = rng.random((n, k)) < 0.6
    out, w = m.attention(Q, K, V, mask)
    out2, w2 = m.attention_loop(Q, K, V, mask)
    assert np.allclose(out, out2) and np.allclose(w, w2)
    s = Q @ K.T / math.sqrt(d)                # independent reference
    for i in range(n):
        if mask[i].any():
            e = np.where(mask[i], np.exp(s[i] - s[i][mask[i]].max()), 0.0)
            assert np.allclose(w[i], e / e.sum())
            assert np.allclose(out[i], (e / e.sum()) @ V)
        else:
            assert np.all(w[i] == 0) and np.all(out[i] == 0)
    assert np.all(w[~mask] == 0)


def test_fully_masked_row_is_zero_not_nan(load):
    m = load("ex01_scaled_dot_product_attention")
    rng = np.random.default_rng(1)
    Q, K, V = rng.standard_normal((3, 4)), rng.standard_normal((3, 4)), rng.standard_normal((3, 2))
    mask = np.array([[True, False, False], [False, False, False], [True, True, True]])
    out, w = m.attention(Q, K, V, mask)
    assert not np.isnan(out).any()
    assert np.all(out[1] == 0) and np.allclose(w.sum(1), [1, 0, 1])
    _, wn = m.attention_large_negative(Q, K, V, mask)
    assert np.allclose(wn[1], 1 / 3)          # the leak the -1e9 trick causes


def test_large_scores_and_batched_shapes(load):
    m = load("ex01_scaled_dot_product_attention")
    _, w = m.attention(np.full((1, 4), 1000.0), np.full((3, 4), 1000.0), np.eye(3))
    assert np.allclose(w, 1 / 3)
    rng = np.random.default_rng(2)
    Q, K, V = (rng.standard_normal((2, 3, 5, 4)) for _ in range(3))
    causal = np.tril(np.ones((5, 5), bool))
    out, w = m.attention(Q, K, V, causal)
    assert out.shape == (2, 3, 5, 4) and np.all(w[..., 0, 1:] == 0)
    for b in range(2):
        for h in range(3):
            assert np.allclose(out[b, h], m.attention_loop(Q[b, h], K[b, h], V[b, h], causal)[0])


def test_scaling_keeps_unit_std(load):
    m = load("ex01_scaled_dot_product_attention")
    rng = np.random.default_rng(0)
    assert abs(m.score_std(256, True, rng) - 1) < 0.1
    assert abs(m.score_std(256, False, rng) - 16) < 1.5


def test_against_torch_sdpa(load):
    torch = pytest.importorskip("torch")
    F = torch.nn.functional
    m = load("ex01_scaled_dot_product_attention")
    rng = np.random.default_rng(3)
    Q, K, V = rng.standard_normal((2, 4, 6)), rng.standard_normal((2, 7, 6)), rng.standard_normal((2, 7, 3))
    mask = rng.random((4, 7)) < 0.7
    mask[:, 0] = True
    ref = F.scaled_dot_product_attention(*(torch.from_numpy(a) for a in (Q, K, V)),
                                         attn_mask=torch.from_numpy(mask))
    assert np.allclose(ref.numpy(), m.attention(Q, K, V, mask)[0])


def test_torch_mha_masked_row_is_path_dependent(load):
    pytest.importorskip("torch")
    m = load("ex01_scaled_dot_product_attention")
    assert m.torch_mha_masked_row_is_nan(need_weights=True, training=True, grad=True)
    assert not m.torch_mha_masked_row_is_nan(need_weights=False, training=True, grad=True)
