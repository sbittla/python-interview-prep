import random
import string

import pytest


def test_examples(load):
    m = load("ex11_char_tools")
    assert m.first_unique("swiss") == 1
    assert m.shift_letters("Hello, World!", 3) == "Khoor, Zruog!"
    assert m.letter_profile("Abba")[:3] == (2, 2, 0)


@pytest.mark.parametrize("s, expected", [("", -1), ("a", 0), ("aa", -1), ("abab", -1), ("aab", 2)])
def test_first_unique_edges(load, s, expected):
    m = load("ex11_char_tools")
    assert m.first_unique(s) == expected == m.brute_force_first_unique(s)


@pytest.mark.parametrize("s, k, expected", [
    ("", 5, ""), ("z", 1, "a"), ("Z", 1, "A"), ("a", -27, "z"), ("abc", 26, "abc"),
    ("é-1 x", 1, "é-1 y"),
])
def test_shift_edges(load, s, k, expected):
    m = load("ex11_char_tools")
    assert m.shift_letters(s, k) == expected == m.shift_with_translate(s, k)


def test_shift_roundtrip(load):
    m = load("ex11_char_tools")
    rng = random.Random(11)
    for _ in range(200):
        s = "".join(rng.choice(string.printable) for _ in range(rng.randint(0, 20)))
        k = rng.randint(-60, 60)
        assert m.shift_letters(m.shift_letters(s, k), -k) == s
        assert m.shift_letters(s, k) == m.shift_with_translate(s, k)


def test_profile(load):
    m = load("ex11_char_tools")
    assert m.letter_profile("") == (0,) * 26
    assert m.letter_profile("z" * 12)[-1] == 12
    assert m.letter_profile("a" * 10) != m.letter_profile("a" * 12)   # no lossy cap
    assert m.letter_profile("Listen!") == m.letter_profile("silent")
    assert len(m.letter_profile("hello world")) == 26
