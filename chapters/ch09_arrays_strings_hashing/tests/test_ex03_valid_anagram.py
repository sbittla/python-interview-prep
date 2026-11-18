import random

import pytest


def test_examples(load):
    m = load("ex03_valid_anagram")
    assert m.solve("listen", "silent") is True
    assert m.solve("rat", "car") is False


@pytest.mark.parametrize("s, t, expected", [
    ("", "", True), ("a", "A", False), ("ab", "a", False), ("aab", "abb", False), ("a b", "b a", True),
])
def test_edge_cases(load, s, t, expected):
    m = load("ex03_valid_anagram")
    assert m.solve(s, t) is expected
    assert m.brute_force(s, t) is expected
    assert m.by_sorting(s, t) is expected
    assert m.by_counter(s, t) is expected


def test_random(load):
    m = load("ex03_valid_anagram")
    rng = random.Random(3)
    for _ in range(200):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 6)))
        if rng.random() < 0.5:
            t = "".join(rng.sample(s, len(s)))
        else:
            t = "".join(rng.choice("abc") for _ in range(len(s)))
        assert m.solve(s, t) == (sorted(s) == sorted(t))
