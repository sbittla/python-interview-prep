import random

import pytest


def test_examples(load):
    m = load("ex06_count_bits_power_two")
    assert m.count_bits(5) == [0, 1, 1, 2, 1, 2]
    assert [m.is_power_of_two(x) for x in (0, 1, 6, 8, -8)] == [False, True, False, True, False]


def test_count_bits_matches_naive(load):
    m = load("ex06_count_bits_power_two")
    assert m.count_bits(0) == [0]
    assert m.count_bits(4096) == m.count_bits_naive(4096) == [bin(i).count("1") for i in range(4097)]


@pytest.mark.parametrize("fn", ["popcount", "popcount_shift", "popcount_kernighan", "count_bits", "count_bits_naive"])
def test_negative_raises_in_every_rung(load, fn):
    with pytest.raises(ValueError):
        getattr(load("ex06_count_bits_power_two"), fn)(-1)


def test_popcount_random_big(load):
    m = load("ex06_count_bits_power_two")
    rng = random.Random(8)
    for _ in range(300):
        x = rng.getrandbits(rng.randint(0, 200))
        expected = bin(x).count("1")
        assert m.popcount(x) == m.popcount_shift(x) == m.popcount_kernighan(x) == expected


def test_power_of_two(load):
    m = load("ex06_count_bits_power_two")
    powers = {1 << k for k in range(130)}
    for x in list(range(-100, 5000)) + [2**129, 2**129 + 1, 2**129 - 1]:
        assert m.is_power_of_two(x) == m.is_power_of_two_loop(x) == (x in powers)
