import math

import numpy as np
import pytest


def test_example_and_loop(load):
    m = load("ex04_positional_encodings")
    expected = [[0, 1, 0, 1], [math.sin(1), math.cos(1), math.sin(0.01), math.cos(0.01)]]
    assert np.allclose(m.sinusoidal(2, 4), expected)
    assert np.allclose(m.sinusoidal(20, 10), m.sinusoidal_loop(20, 10))


def test_odd_d_raises(load):
    m = load("ex04_positional_encodings")
    for f in (lambda: m.sinusoidal(3, 5), lambda: m.rope(np.ones((2, 3)), [0, 1])):
        with pytest.raises(ValueError):
            f()


@pytest.mark.parametrize("k", [1, 5, 13])
def test_sinusoid_shift_is_linear(load, k):
    m = load("ex04_positional_encodings")
    pe = m.sinusoidal(40, 12)
    assert np.allclose(pe[k:], pe[:-k] @ m.shift_matrix(k, 12).T)


def test_rope_d2_is_plain_rotation(load):
    m = load("ex04_positional_encodings")
    assert np.allclose(m.rope(np.array([[1.0, 0.0]]), [3]), [[math.cos(3), math.sin(3)]])
    # second pair of d=4 rotates by p * 10000^(-1/2) = p / 100
    assert np.allclose(m.rope(np.array([[0.0, 0.0, 1.0, 0.0]]), [5]), [[0, 0, math.cos(0.05), math.sin(0.05)]])


def test_rope_relative_and_norm(load):
    m = load("ex04_positional_encodings")
    rng = np.random.default_rng(4)
    q, k = rng.standard_normal(16), rng.standard_normal(16)

    def s(a, b):
        return float(m.rope(q[None], [a])[0] @ m.rope(k[None], [b])[0])

    for a, b in [(7, 3), (50, 46), (4, 0)]:
        assert math.isclose(s(a, b), s(10, 6), rel_tol=1e-9, abs_tol=1e-9)
    assert not math.isclose(s(3, 7), s(7, 3))
    x = rng.standard_normal((2, 5, 16))
    r = m.rope(x, np.arange(5))
    assert np.allclose(np.linalg.norm(r, axis=-1), np.linalg.norm(x, axis=-1))
    assert np.allclose(r[:, 0], x[:, 0]) and not np.allclose(r[:, 1], x[:, 1])


def test_half_split_equivalence(load):
    m = load("ex04_positional_encodings")
    x = np.random.default_rng(5).standard_normal((6, 8))
    p = m.interleaved_to_half(8)
    assert p.tolist() == [0, 2, 4, 6, 1, 3, 5, 7]
    assert np.allclose(m.rope_half(x[:, p], np.arange(6)), m.rope(x, np.arange(6))[:, p])
