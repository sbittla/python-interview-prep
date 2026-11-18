import random

import pytest


def test_examples(load):
    m = load("ex09_longest_palindromic_substring")
    assert m.solve("babad") == "bab"
    assert m.solve("cbbd") == "bb"


@pytest.mark.parametrize("s, expected", [
    ("", ""), ("a", "a"), ("ac", "a"), ("aaaa", "aaaa"), ("forgeeksskeegfor", "geeksskeeg"),
])
def test_edge_cases(load, s, expected):
    assert load("ex09_longest_palindromic_substring").solve(s) == expected


def test_count(load):
    m = load("ex09_longest_palindromic_substring")
    assert m.count_palindromes("aaa") == 6
    assert m.count_palindromes("abc") == 3


def test_random_against_brute(load):
    m = load("ex09_longest_palindromic_substring")
    rng = random.Random(9)
    for _ in range(300):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 10)))
        assert m.solve(s) == m.brute_force(s) == m.dp_table(s)
