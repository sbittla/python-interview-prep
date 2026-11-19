import random

import pytest

NAME = "ex09_min_window_substring"


def test_examples(load):
    m = load(NAME)
    assert m.solve("ADOBECODEBANC", "ABC") == "BANC"
    assert m.solve("a", "aa") == ""


@pytest.mark.parametrize("s, t, expected", [
    ("", "a", ""), ("abc", "", ""), ("a", "a", "a"), ("aa", "aa", "aa"), ("bbaac", "aba", "baa"),
    ("abab", "ab", "ab"), ("aA", "A", "A"), ("cabwefgewcwaefgcf", "cae", "cwae"),
])
def test_edge_cases(load, s, t, expected):
    assert load(NAME).solve(s, t) == expected


def test_random_all_rungs_agree(load):
    m = load(NAME)
    rng = random.Random(1009)
    for _ in range(400):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 12)))
        t = "".join(rng.choice("abc") for _ in range(rng.randint(0, 4)))
        want = m.brute_force(s, t)
        assert m.solve(s, t) == want
        assert m.extend_each_start(s, t) == want


def test_wrong_missing_counter(load):
    m = load(NAME)
    assert m.wrong_any_required("bbaac", "aba") == "bba"
