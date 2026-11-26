import numpy as np
import pytest

LG = np.log(np.array([0.5, 0.25, 0.125, 0.125]))


def kept(a):
    return np.isfinite(a).astype(int).tolist()


@pytest.mark.parametrize("p, expected", [
    (0.1, [1, 0, 0, 0]), (0.5, [1, 0, 0, 0]), (0.6, [1, 1, 0, 0]), (0.75, [1, 1, 0, 0]),
    (0.8, [1, 1, 1, 0]), (0.9, [1, 1, 1, 1]), (1.0, [1, 1, 1, 1]),
])
def test_top_p_boundary(load, p, expected):
    m = load("ex09_sampling")
    assert kept(m.top_p_filter(LG, p)) == expected
    assert kept(m.top_p_loop(LG, p)) == expected


def test_top_p_wrong_variant_differs(load):
    m = load("ex09_sampling")
    assert kept(m.top_p_wrong_le(LG, 0.6)) == [1, 0, 0, 0]


def test_top_p_unsorted_input_and_values_kept(load):
    m = load("ex09_sampling")
    z = np.array([0.0, 3.0, 1.0, 2.0])
    out = m.top_p_filter(z, 0.7)
    assert kept(out) == [0, 1, 0, 1] and out[1] == 3.0 and out[3] == 2.0
    with pytest.raises(ValueError):
        m.top_p_filter(z, 0.0)


def test_top_k(load):
    m = load("ex09_sampling")
    z = np.array([2.0, 1.0, 0.5, 0.5, -1.0])
    assert kept(m.top_k_filter(z, 1)) == [1, 0, 0, 0, 0]
    assert kept(m.top_k_filter(z, 2)) == [1, 1, 0, 0, 0]
    assert kept(m.top_k_filter(z, 3)) == [1, 1, 1, 1, 0]       # tie at the boundary kept
    assert kept(m.top_k_filter(z, 9)) == [1, 1, 1, 1, 1]
    with pytest.raises(ValueError):
        m.top_k_filter(z, 0)


def test_temperature_and_greedy(load):
    m = load("ex09_sampling")
    z = np.array([1.0, 3.0, 3.0, 0.0])
    assert m.greedy(z) == 1
    assert np.allclose(m.apply_temperature(z, 2.0), z / 2)
    with pytest.raises(ValueError):
        m.apply_temperature(z, 0.0)
    cold = m.filtered_probs(z, 0.01)
    assert np.allclose(cold, [0, 0.5, 0.5, 0], atol=1e-6)
    hot = m.filtered_probs(z, 1000.0)
    assert np.allclose(hot, 0.25, atol=1e-3)


def test_order_temperature_then_filters(load):
    m = load("ex09_sampling")
    z = np.array([2.0, 1.0, 0.5, 0.5, -1.0, -3.0])
    assert (m.filtered_probs(z, 1.0, top_p=0.8) > 0).astype(int).tolist() == [1, 1, 1, 0, 0, 0]
    assert (m.filtered_probs(z, 4.0, top_p=0.8) > 0).astype(int).tolist() == [1, 1, 1, 1, 0, 0]
    p = m.filtered_probs(z, 1.0, top_k=2)
    e = np.exp([2.0, 1.0])
    assert np.allclose(p, [e[0] / e.sum(), e[1] / e.sum(), 0, 0, 0, 0])


def test_sampler_frequencies_and_seed(load):
    m = load("ex09_sampling")
    z = np.array([1.0, 0.2, -0.5, 0.9, -2.0])
    target = m.filtered_probs(z, 0.9, top_k=4, top_p=0.95)
    rng = np.random.default_rng(11)
    draws = np.array([m.sample(z, rng, 0.9, top_k=4, top_p=0.95) for _ in range(30000)])
    freq = np.bincount(draws, minlength=5) / draws.size
    assert np.abs(freq - target).max() < 0.01
    assert freq[target == 0].sum() == 0
    a = [m.sample(z, np.random.default_rng(5)) for _ in range(3)]
    assert len(set(a)) == 1


def test_single_token_vocab(load):
    m = load("ex09_sampling")
    z = np.array([0.3])
    assert m.sample(z, np.random.default_rng(0), top_k=5, top_p=0.1) == 0
