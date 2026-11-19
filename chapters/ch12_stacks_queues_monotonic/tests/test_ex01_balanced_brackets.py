import random

import pytest


def test_examples(load):
    m = load("ex01_balanced_brackets")
    assert m.first_error("f(a[i]) + {b}") == -1
    assert m.first_error("(]") == 1
    assert m.first_error("x = (a + [b)") == 11
    assert m.first_error("((a)") == 0


@pytest.mark.parametrize("s, expected", [
    ("", -1), ("abc", -1), (")", 0), ("(", 0), (")(", 0), ("([)]", 2), ("{[()()]}", -1),
    ("((", 0), ("(()))", 4), ("a)b", 1), ("[(])", 2), ("}{", 0),
])
def test_edge_cases(load, s, expected):
    assert load("ex01_balanced_brackets").first_error(s) == expected


def test_random_against_brute(load):
    m = load("ex01_balanced_brackets")
    rng = random.Random(12)
    for _ in range(500):
        s = "".join(rng.choice("()[]{}x") for _ in range(rng.randint(0, 12)))
        assert m.first_error(s) == m.brute_force(s), s
