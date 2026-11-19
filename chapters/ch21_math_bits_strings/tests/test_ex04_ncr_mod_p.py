import math
import random

import pytest


def test_examples(load):
    m = load("ex04_ncr_mod_p")
    assert m.pascal_row(5) == [1, 5, 10, 10, 5, 1]
    assert m.Binomial(10, 10**9 + 7).comb(10, 3) == 120
    assert m.lucas(10**18, 10**9, 13) == 0


def test_pascal_rows_exact(load):
    m = load("ex04_ncr_mod_p")
    for n in range(60):
        assert m.pascal_row(n) == [math.comb(n, k) for k in range(n + 1)]
    with pytest.raises(ValueError):
        m.pascal_row(-1)


@pytest.mark.parametrize("mod", [1, 2, 4, 6, 7, 10**9 + 7])
def test_table_any_modulus(load, mod):
    t = load("ex04_ncr_mod_p").ncr_table(30, mod)
    assert all(t[i][j] == math.comb(i, j) % mod for i in range(31) for j in range(i + 1))


def test_binomial_queries(load):
    m = load("ex04_ncr_mod_p")
    p = 1_000_003
    b = m.Binomial(2000, p)
    rng = random.Random(5)
    for _ in range(500):
        n, k = rng.randint(0, 2000), rng.randint(-3, 2003)
        expected = math.comb(n, k) % p if k >= 0 else 0
        assert b.comb(n, k) == expected
    with pytest.raises(ValueError):
        m.Binomial(10, 7)


def test_lucas(load):
    m = load("ex04_ncr_mod_p")
    rng = random.Random(6)
    for _ in range(300):
        p = rng.choice([2, 3, 5, 7, 13, 101])
        n, k = rng.randint(0, 3000), rng.randint(-2, 3000)
        expected = math.comb(n, k) % p if k >= 0 else 0
        assert m.lucas(n, k, p) == expected
