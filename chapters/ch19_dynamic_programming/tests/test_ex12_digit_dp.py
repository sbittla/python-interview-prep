import random

import pytest

M = "ex12_digit_dp"


def test_examples(load):
    m = load(M)
    assert (m.count_no_repeat(20), m.count_no_repeat(100)) == (19, 90)
    assert m.count_range(100, 200) == 81


@pytest.mark.parametrize("n, expected", [
    (-5, 0), (0, 0), (1, 1), (9, 9), (10, 10), (11, 10), (12, 11), (99, 90), (100, 90),
    (121, 101), (1000, 819),
])
def test_edges(load, n, expected):
    m = load(M)
    assert m.count_no_repeat(n) == m.count_memo(n) == expected
    assert m.count_brute(max(n, 0)) == expected


def test_powers_of_ten_closed_form(load):
    m = load(M)
    for k in range(1, 19):                     # all numbers with < k+1 digits: 9 + 81 + ...
        assert m.count_no_repeat(10 ** k - 1) == sum(9 ** j for j in range(1, k + 1))


def test_random_against_brute(load):
    m = load(M)
    rng = random.Random(43)
    for _ in range(100):
        n = rng.randint(0, 5000)
        assert m.count_no_repeat(n) == m.count_memo(n) == m.count_recursive(n) == m.count_brute(n)


def test_huge_n_rungs_agree(load):
    m = load(M)
    rng = random.Random(47)
    for _ in range(20):
        n = rng.randint(10 ** 15, 10 ** 18)
        assert m.count_no_repeat(n) == m.count_memo(n)


@pytest.mark.parametrize("lo, hi, expected", [(100, 200, 81), (5, 5, 1), (11, 11, 0), (9, 3, 0), (1, 20, 19)])
def test_count_range(load, lo, hi, expected):
    assert load(M).count_range(lo, hi) == expected
