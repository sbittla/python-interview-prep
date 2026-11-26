import numpy as np
import pytest


def test_examples(load):
    m = load("ex03_causal_padding_masks")
    assert m.causal_mask(2, 4).astype(int).tolist() == [[1, 1, 1, 0], [1, 1, 1, 1]]
    assert m.padding_mask([2, 3], 3, "left").astype(int).tolist() == [[0, 1, 1], [1, 1, 1]]
    assert m.padding_mask([2, 0], 3).astype(int).tolist() == [[1, 1, 0], [0, 0, 0]]


@pytest.mark.parametrize("n_q, n_k", [(1, 1), (1, 7), (3, 3), (3, 8), (5, 6)])
def test_causal_vs_loop_and_definition(load, n_q, n_k):
    m = load("ex03_causal_padding_masks")
    c = m.causal_mask(n_q, n_k)
    assert c.shape == (n_q, n_k)
    assert np.array_equal(c, m.causal_mask_loop(n_q, n_k))
    for i in range(n_q):
        for j in range(n_k):
            assert c[i, j] == (j <= i + n_k - n_q)
    assert np.array_equal(m.causal_mask(4), np.tril(np.ones((4, 4), bool)))


def test_bad_arguments_raise(load):
    m = load("ex03_causal_padding_masks")
    with pytest.raises(ValueError):
        m.causal_mask(3, 2)
    with pytest.raises(ValueError):
        m.padding_mask([1], 3, "middle")


def test_combine_and_fully_masked(load):
    m = load("ex03_causal_padding_masks")
    right = m.combine(m.causal_mask(4), m.padding_mask([2, 4], 4))
    left = m.combine(m.causal_mask(4), m.padding_mask([2, 4], 4, "left"))
    assert right.shape == (2, 1, 4, 4)
    assert m.fully_masked_rows(right) == []
    assert m.fully_masked_rows(left) == [(0, 0, 0), (0, 0, 1)]
    assert not right[0, 0, 3, 2] and right[1, 0, 3, 2]


def test_causality_by_perturbation(load):
    m = load("ex03_causal_padding_masks")
    rng = np.random.default_rng(0)
    q, k, v = (rng.standard_normal((7, 4)) for _ in range(3))
    cm = m.causal_mask(7)
    base = m.naive_attention(q, k, v, cm)
    for t in range(7):
        k2, v2 = k.copy(), v.copy()
        k2[t:] += 5.0
        v2[t:] -= 5.0
        new = m.naive_attention(q, k2, v2, cm)
        assert np.allclose(new[:t], base[:t]) and not np.allclose(new[t:], base[t:])


def test_naive_softmax_nan_on_left_padding(load):
    m = load("ex03_causal_padding_masks")
    rng = np.random.default_rng(1)
    q, k, v = (rng.standard_normal((4, 2)) for _ in range(3))
    mask = m.combine(m.causal_mask(4), m.padding_mask([2], 4, "left"))[0, 0]
    out = m.naive_attention(q, k, v, mask)
    assert np.isnan(out[:2]).all() and not np.isnan(out[2:]).any()


def test_additive_mask(load):
    m = load("ex03_causal_padding_masks")
    a = m.additive_mask(m.causal_mask(3))
    assert a[0].tolist() == [0.0, -np.inf, -np.inf] and a[2].tolist() == [0.0, 0.0, 0.0]
