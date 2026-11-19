import random
from math import perm

import pytest


def test_examples(load):
    m = load("ex06_itertools_reports")
    assert m.longest_outage(["up", "down", "down", "up", "down"]) == (1, 2)
    assert m.lowest_balance(100, [-30, 50, -90, 10]) == 30
    assert m.affordable_pairs({"tea": 3, "cake": 5, "pie": 9}, 9) == [("cake", "tea")]
    assert (m.count_codes("123", 2, repeat=True), m.count_codes("123", 2, repeat=False)) == (9, 6)


@pytest.mark.parametrize("statuses, expected", [
    ([], (-1, 0)),
    (["up"], (-1, 0)),
    (["down"], (0, 1)),
    (["down", "up", "down"], (0, 1)),          # earliest on ties
    (["up", "down", "down", "down"], (1, 3)),  # run reaching the end
])
def test_outage_edges(load, statuses, expected):
    m = load("ex06_itertools_reports")
    assert m.longest_outage(statuses) == expected == m.brute_force_outage(statuses)


def test_outage_random(load):
    m = load("ex06_itertools_reports")
    rng = random.Random(6)
    for _ in range(300):
        s = [rng.choice(["up", "down"]) for _ in range(rng.randint(0, 12))]
        assert m.longest_outage(s) == m.brute_force_outage(s)


def test_balance(load):
    m = load("ex06_itertools_reports")
    assert m.lowest_balance(5, []) == 5
    assert m.lowest_balance(0, [10, 20]) == 0
    rng = random.Random(66)
    for _ in range(100):
        d = [rng.randint(-10, 10) for _ in range(rng.randint(0, 10))]
        assert m.lowest_balance(3, d) == m.brute_force_balance(3, d)


def test_pairs_and_codes(load):
    m = load("ex06_itertools_reports")
    assert m.affordable_pairs({}, 10) == []
    assert m.affordable_pairs({"a": 1}, 10) == []
    assert m.affordable_pairs({"b": 2, "a": 2}, 4) == [("a", "b")]
    for d in range(1, 5):
        for length in range(0, d + 1):
            digits = "0123456789"[:d]
            assert m.count_codes(digits, length, True) == d ** length
            assert m.count_codes(digits, length, False) == perm(d, length)
    assert m.count_codes("1122", 2, True) == 4    # distinct characters only
