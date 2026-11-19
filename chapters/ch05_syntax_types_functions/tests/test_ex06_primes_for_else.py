import pytest


def test_small_primes(load):
    m = load("ex06_primes_for_else")
    assert [n for n in range(-3, 30) if m.is_prime(n)] == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


@pytest.mark.parametrize("n, expected", [
    (1_000_000_007, True), (2**31 - 1, True), (1_000_000_007 * 3, False),
    (49, False), (97 * 89, False), (2, True), (1, False),
])
def test_big_and_squares(load, n, expected):
    assert load("ex06_primes_for_else").is_prime(n) is expected


@pytest.mark.parametrize("nums, expected", [
    ([4, 6, 9, 11, 13], 11), ([1, 4, 6], None), ([], None), ([2], 2), (iter([8, 10, 17, 19]), 17),
])
def test_first_prime(load, nums, expected):
    assert load("ex06_primes_for_else").solve(nums) == expected
