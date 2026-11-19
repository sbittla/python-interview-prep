import math
import random
from fractions import Fraction

import pytest


def test_examples(load):
    m = load("ex01_gcd_lcm_fractions")
    assert (m.gcd_euclid(48, 18), m.gcd_euclid(-4, 6), m.gcd_euclid(0, 0)) == (6, 2, 0)
    assert (m.gcd_list([12, 18, 30]), m.lcm_list([4, 6, 10])) == (6, 60)
    assert m.reduce_fraction(6, -8) == (-3, 4)


@pytest.mark.parametrize("nums, g, l", [([], 0, 1), ([0], 0, 0), ([0, 5], 5, 0), ([-4, 6], 2, 12), ([7], 7, 7)])
def test_list_edge_cases(load, nums, g, l):
    m = load("ex01_gcd_lcm_fractions")
    assert m.gcd_list(nums) == g and m.lcm_list(nums) == l


def test_zero_denominator(load):
    with pytest.raises(ZeroDivisionError):
        load("ex01_gcd_lcm_fractions").reduce_fraction(3, 0)


def test_random_against_math(load):
    m = load("ex01_gcd_lcm_fractions")
    rng = random.Random(1)
    for _ in range(400):
        a, b = rng.randint(-200, 200), rng.randint(-200, 200)
        assert m.gcd_euclid(a, b) == m.gcd_brute(a, b) == math.gcd(a, b)
        nums = [rng.randint(-50, 50) for _ in range(rng.randint(0, 5))]
        assert m.gcd_list(nums) == math.gcd(*nums)
        assert m.lcm_list(nums) == math.lcm(*nums)
        if b:
            f = Fraction(a, b)
            assert m.reduce_fraction(a, b) == (f.numerator, f.denominator)


def test_big_values(load):
    m = load("ex01_gcd_lcm_fractions")
    a, b = 2**200 * 3**50, 2**150 * 3**80 * 7
    assert m.gcd_euclid(a, b) == math.gcd(a, b) == 2**150 * 3**50
