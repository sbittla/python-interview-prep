import random

import pytest


def test_examples(load):
    m = load("ex05_partition_labels")
    assert m.partition_labels("abacbdefegde") == [5, 7]
    assert m.partition_labels("ababcbacadefegdehijhklij") == [9, 7, 8]


@pytest.mark.parametrize("s, expected", [("a", [1]), ("abc", [1, 1, 1]), ("aaaa", [4]), ("abcba", [5])])
def test_edge_cases(load, s, expected):
    assert load("ex05_partition_labels").partition_labels(s) == expected


def test_random_against_brute_force(load):
    m = load("ex05_partition_labels")
    rng = random.Random(5)
    for _ in range(200):
        s = "".join(rng.choice("abcde") for _ in range(rng.randint(1, 15)))
        assert m.partition_labels(s) == m.brute_force(s)
        assert "".join(m.pieces(s)) == s
