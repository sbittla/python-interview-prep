import math
import random

import pytest


def test_examples(load):
    m = load("ex02_sieve_factorise")
    assert m.sieve(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert m.factorise(360, m.spf_table(400)) == [2, 2, 2, 3, 3, 5]
    assert m.segmented_sieve(100, 130) == [101, 103, 107, 109, 113, 127]


@pytest.mark.parametrize("n, expected", [(-5, []), (0, []), (1, []), (2, [2]), (3, [2, 3]), (4, [2, 3])])
def test_small_n(load, n, expected):
    m = load("ex02_sieve_factorise")
    assert m.sieve(n) == m.primes_trial(n) == expected


def test_sieve_matches_trial_division(load):
    m = load("ex02_sieve_factorise")
    assert m.sieve(3000) == m.primes_trial(3000)
    assert len(m.sieve(10**5)) == 9592


def test_factorise_products(load):
    m = load("ex02_sieve_factorise")
    spf = m.spf_table(5000)
    primes = set(m.sieve(5000))
    assert m.factorise(1, spf) == []
    for x in range(2, 5001):
        fs = m.factorise(x, spf)
        assert math.prod(fs) == x and fs == sorted(fs) and set(fs) <= primes
    for bad in (0, 5001):
        with pytest.raises(ValueError):
            m.factorise(bad, spf)


def test_segmented_random_windows(load):
    m = load("ex02_sieve_factorise")
    rng = random.Random(2)
    primes = set(m.sieve(20000))
    for _ in range(100):
        lo = rng.randint(-5, 19000)
        hi = min(lo + rng.randint(-3, 900), 20000)
        assert m.segmented_sieve(lo, hi) == [p for p in range(lo, hi + 1) if p in primes]


def test_segmented_large(load):
    m = load("ex02_sieve_factorise")
    got = m.segmented_sieve(10**12, 10**12 + 100)
    assert got == [1000000000039, 1000000000061, 1000000000063, 1000000000091]
