import random

import pytest


def test_examples(load):
    m = load("ex08_valid_palindrome")
    assert m.solve("A man, a plan, a canal: Panama") is True
    assert m.solve("race a car") is False
    assert m.solve_one_delete("abca") is True


@pytest.mark.parametrize("s, expected", [("", True), (" ", True), (".,", True), ("0P", False), ("ab_a", True)])
def test_edge_cases(load, s, expected):
    m = load("ex08_valid_palindrome")
    assert m.solve(s) is expected
    assert m.brute_force(s) is expected


@pytest.mark.parametrize("s, expected", [("abc", False), ("deeee", True), ("", True), ("cbbcc", True), ("abcda", False)])
def test_one_delete(load, s, expected):
    assert load("ex08_valid_palindrome").solve_one_delete(s) is expected


def _one_delete_reference(t: str) -> bool:
    if t == t[::-1]:
        return True
    for i in range(len(t)):
        u = t[:i] + t[i + 1:]
        if u == u[::-1]:
            return True
    return False


def test_random(load):
    m = load("ex08_valid_palindrome")
    rng = random.Random(8)
    for _ in range(300):
        s = "".join(rng.choice("aAb ,1") for _ in range(rng.randint(0, 8)))
        assert m.solve(s) == m.brute_force(s)
        t = "".join(rng.choice("ab") for _ in range(rng.randint(0, 7)))
        assert m.solve_one_delete(t) == _one_delete_reference(t)
