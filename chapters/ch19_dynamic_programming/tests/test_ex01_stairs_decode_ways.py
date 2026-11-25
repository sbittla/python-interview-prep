import random

import pytest

M = "ex01_stairs_decode_ways"


def test_examples(load):
    m = load(M)
    assert (m.count_ways(5), m.count_ways(4, (1, 3, 5))) == (8, 3)
    assert m.min_cost_climb([10, 15, 20]) == 15
    assert (m.decode_ways("226"), m.decode_ways("06"), m.decode_ways("11106")) == (3, 0, 2)


@pytest.mark.parametrize("n, steps, expected", [
    (0, (1, 2), 1), (1, (1, 2), 1), (2, (2,), 1), (3, (2,), 0), (10, (1, 2), 89),
    (3, (1, 2, 3), 4), (7, (3, 5), 0), (8, (3, 5), 2),
])
def test_count_ways_edges(load, n, steps, expected):
    m = load(M)
    assert m.count_ways(n, steps) == expected
    assert m.count_ways_table(n, steps) == m.count_ways_memo(n, steps) == expected


def test_count_ways_large_is_exact_fibonacci(load):
    m = load(M)
    a, b = 1, 1                                 # ways(0), ways(1)
    for _ in range(299):
        a, b = b, a + b
    assert m.count_ways(300) == b               # far beyond 64 bits; exact int


def test_count_ways_random_against_brute(load):
    m = load(M)
    rng = random.Random(19)
    for _ in range(60):
        steps = tuple(sorted(rng.sample(range(1, 6), rng.randint(1, 3))))
        n = rng.randint(0, 18)
        assert m.count_ways(n, steps) == m.count_ways_brute(n, steps)


@pytest.mark.parametrize("cost, expected", [
    ([], 0), ([5], 0), ([5, 3], 3), ([1, 100, 1, 1, 1, 100, 1, 1, 100, 1], 6), ([0, 0, 0], 0),
])
def test_min_cost_climb(load, cost, expected):
    m = load(M)
    assert m.min_cost_climb(cost) == m.min_cost_climb_brute(cost) == expected


@pytest.mark.parametrize("s, expected", [
    ("", 1), ("0", 0), ("1", 1), ("10", 1), ("20", 1), ("30", 0), ("27", 1), ("26", 2),
    ("100", 0), ("101", 1), ("2101", 1), ("1111111111", 89), ("01", 0),
])
def test_decode_ways_edges(load, s, expected):
    m = load(M)
    assert m.decode_ways(s) == expected
    assert m.decode_ways_table(s) == m.decode_ways_memo(s) == m.decode_ways_brute(s) == expected


def test_decode_ways_random(load):
    m = load(M)
    rng = random.Random(7)
    for _ in range(300):
        s = "".join(rng.choice("0122367") for _ in range(rng.randint(0, 14)))
        assert m.decode_ways(s) == m.decode_ways_table(s) == m.decode_ways_brute(s)


def test_decode_ways_long_input_no_recursion(load):
    m = load(M)
    assert m.decode_ways("1" * 5000) == m.decode_ways_table("1" * 5000) > 0
