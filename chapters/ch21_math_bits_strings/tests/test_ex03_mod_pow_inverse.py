import math
import random

import pytest


def test_examples(load):
    m = load("ex03_mod_pow_inverse")
    assert m.mod_pow(3, 200, 13) == pow(3, 200, 13) == 9
    assert m.mod_inverse(3, 11) == pow(3, -1, 11) == 4


@pytest.mark.parametrize("a, b, mod", [(0, 0, 7), (5, 0, 1), (0, 0, 1), (-2, 3, 5), (10**20, 10**18, 10**9 + 7)])
def test_edge_cases(load, a, b, mod):
    m = load("ex03_mod_pow_inverse")
    assert m.mod_pow(a, b, mod) == m.mod_pow_recursive(a, b, mod) == pow(a, b, mod)


@pytest.mark.parametrize("fn", ["mod_pow", "mod_pow_recursive", "mod_pow_naive"])
@pytest.mark.parametrize("args", [(2, -1, 5), (2, 3, 0), (2, 3, -4)])
def test_invalid_inputs_same_in_every_rung(load, fn, args):
    with pytest.raises(ValueError):
        getattr(load("ex03_mod_pow_inverse"), fn)(*args)


def test_random_against_builtin(load):
    m = load("ex03_mod_pow_inverse")
    rng = random.Random(3)
    for _ in range(500):
        a, b, mod = rng.randint(-10**6, 10**6), rng.randint(0, 300), rng.randint(1, 10**6)
        expected = pow(a, b, mod)
        assert m.mod_pow(a, b, mod) == m.mod_pow_recursive(a, b, mod) == m.mod_pow_naive(a, b, mod) == expected


def test_ext_gcd_and_inverse(load):
    m = load("ex03_mod_pow_inverse")
    rng = random.Random(4)
    for _ in range(500):
        a, b = rng.randint(-10**6, 10**6), rng.randint(-10**6, 10**6)
        g, x, y = m.ext_gcd(a, b)
        assert g == math.gcd(a, b) and a * x + b * y == g
        mod = rng.randint(1, 1000)
        if math.gcd(a, mod) == 1:
            inv = m.mod_inverse(a, mod)
            assert inv == pow(a, -1, mod) and 0 <= inv < mod
        else:
            with pytest.raises(ValueError):
                m.mod_inverse(a, mod)
