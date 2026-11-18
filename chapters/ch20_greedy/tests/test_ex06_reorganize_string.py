import random
from collections import Counter

import pytest


def test_examples(load):
    m = load("ex06_reorganize_string")
    assert m.reorganize("aab") == "aba"
    assert m.reorganize("aaab") == ""


@pytest.mark.parametrize("s, possible", [("a", True), ("aa", False), ("aaabb", True), ("aaabbc", True), ("aaaab", False)])
def test_edge_cases(load, s, possible):
    m = load("ex06_reorganize_string")
    r = m.reorganize(s)
    assert bool(r) is possible
    if possible:
        assert m.is_valid(r) and Counter(r) == Counter(s)


def test_random_feasibility_matches_brute(load):
    m = load("ex06_reorganize_string")
    rng = random.Random(6)
    for _ in range(150):
        s = "".join(rng.choice("aabc") for _ in range(rng.randint(1, 7)))
        expected_possible = bool(m.brute_force(s))
        for f in (m.reorganize, m.reorganize_even_odd):
            r = f(s)
            assert bool(r) == expected_possible
            if r:
                assert m.is_valid(r) and Counter(r) == Counter(s)
