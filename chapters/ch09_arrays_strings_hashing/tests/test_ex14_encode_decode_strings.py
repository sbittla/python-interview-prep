import random

import pytest


def test_examples(load):
    m = load("ex14_encode_decode_strings")
    assert m.encode(["hi", "", "a#b"]) == "2#hi0#3#a#b"
    assert m.decode("2#hi0#3#a#b") == ["hi", "", "a#b"]


@pytest.mark.parametrize("strs", [[], [""], ["", ""], ["12#", "#", "3"], ["héllo", "日本"], ["a" * 15]])
def test_round_trip(load, strs):
    assert load("ex14_encode_decode_strings").solve(strs) == strs


def test_random_round_trip(load):
    m = load("ex14_encode_decode_strings")
    rng = random.Random(14)
    for _ in range(200):
        strs = ["".join(rng.choice("ab#1, ") for _ in range(rng.randint(0, 12))) for _ in range(rng.randint(0, 5))]
        assert m.decode(m.encode(strs)) == strs


@pytest.mark.parametrize("s, enc", [("aaabcc", "3a1b2c"), ("", ""), ("abc", "1a1b1c"), ("a" * 12 + "b", "12a1b")])
def test_rle(load, s, enc):
    m = load("ex14_encode_decode_strings")
    assert m.rle_encode(s) == enc
    assert m.rle_decode(enc) == s
