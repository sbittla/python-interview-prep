import random

import pytest


def test_examples(load):
    m = load("ex05_single_number")
    assert m.single_one([4, 1, 2, 1, 2]) == 4
    assert m.single_three([2, 2, 3, 2]) == 3
    assert m.single_three([-2, -2, 1, 1, -3, 1, -3, -3, -4, -2]) == -4


@pytest.mark.parametrize("fn", ["single_one", "single_three", "single_three_bitcount", "single_brute"])
def test_empty_raises_in_every_rung(load, fn):
    with pytest.raises(ValueError):
        getattr(load("ex05_single_number"), fn)([])


def test_int32_extremes(load):
    m = load("ex05_single_number")
    for x in (-2**31, 2**31 - 1, 0, -1):
        nums = [x] + [7, 7, 7, -9, -9, -9]
        assert m.single_three(nums) == m.single_three_bitcount(nums) == x
    assert m.single_three_bitcount([-1, 5, 5, 5], fix_sign=False) == 2**32 - 1
    assert m.to_int32(-5 & 0xFFFFFFFF) == -5


def test_random_against_counter(load):
    m = load("ex05_single_number")
    rng = random.Random(7)
    for _ in range(300):
        vals = rng.sample(range(-2**31, 2**31), rng.randint(1, 8))
        single, rest = vals[0], vals[1:]
        twice = rest * 2 + [single]
        thrice = rest * 3 + [single]
        rng.shuffle(twice)
        rng.shuffle(thrice)
        assert m.single_one(twice) == m.single_brute(twice) == single
        assert m.single_three(thrice) == m.single_three_bitcount(thrice) == m.single_brute(thrice) == single
