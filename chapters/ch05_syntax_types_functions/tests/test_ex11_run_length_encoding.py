import pytest


@pytest.mark.parametrize("s, code", [
    ("aaabcc", "a3b1c2"), ("", ""), ("a", "a1"), ("abc", "a1b1c1"), ("z" * 12, "z12"), ("aabbaa", "a2b2a2"),
])
def test_encode_decode(load, s, code):
    m = load("ex11_run_length_encoding")
    assert m.solve(s) == code
    assert m.brute_force(s) == code
    assert m.decode(code) == s


def test_decode_multi_digit_and_errors(load):
    m = load("ex11_run_length_encoding")
    assert m.decode("x10y2") == "x" * 10 + "yy"
    with pytest.raises(ValueError):
        m.decode("ab2")


def test_decode_rejects_leading_digit_and_handles_zero(load):
    m = load("ex11_run_length_encoding")
    with pytest.raises(ValueError):
        m.decode("3a")
    assert m.decode("a0b2") == "bb"
    long = "q" * 1000 + "r"
    assert m.decode(m.solve(long)) == long and m.solve(long) == "q1000r1"
