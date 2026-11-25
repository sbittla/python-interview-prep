import random

import pytest


@pytest.fixture
def m(load):
    return load("ex03_span_sequence")


def test_example(m):
    s = m.Span(0, 10, 3)
    assert (len(s), list(s), s[-1], 9 in s, 4 in s) == (4, [0, 3, 6, 9], 9, True, False)
    assert repr(m.Span(0, 20, 2)[1:8:3]) == "Span(2, 16, 6)"


def test_matches_range_randomly(m):
    rng = random.Random(2024)
    for _ in range(400):
        a, b = rng.randint(-20, 20), rng.randint(-20, 20)
        c = rng.choice([-5, -3, -2, -1, 1, 2, 3, 7])
        s, r = m.Span(a, b, c), range(a, b, c)
        assert len(s) == len(r)
        assert list(s) == list(r) and list(reversed(s)) == list(reversed(r))
        for x in range(-25, 26):
            assert (x in s) == (x in r)
        for i in range(-len(r), len(r)):
            assert s[i] == r[i]
        sl = slice(rng.choice([None, -3, 0, 2]), rng.choice([None, -1, 4, 30]),
                   rng.choice([None, 1, 2, -1, -2]))
        sub = s[sl]
        assert isinstance(sub, m.Span) and list(sub) == list(r[sl])


@pytest.mark.parametrize("i", [3, -4, 100])
def test_index_error(m, i):
    with pytest.raises(IndexError):
        m.Span(0, 3)[i]


def test_empty_and_zero_step(m):
    assert len(m.Span(5, 5)) == 0 and list(m.Span(5, 0)) == [] and 5 not in m.Span(5, 5)
    with pytest.raises(ValueError):
        m.Span(0, 5, 0)


def test_contains_non_int(m):
    assert "a" not in m.Span(0, 5) and 2.5 not in m.Span(0, 5)


def test_huge_is_constant_time(m):
    s = m.Span(0, 10**18, 7)
    assert len(s) == len(range(0, 10**18, 7))
    assert 7 * 10**16 in s and 7 * 10**16 + 1 not in s
    assert s[-1] == range(0, 10**18, 7)[-1]


def test_equality_and_hash(m):
    S = m.Span
    assert S(0, 0) == S(5, 5) and S(0, 3, 5) == S(0, 1) and S(0, 10, 2) == S(0, 9, 2)
    assert S(0, 10, 2) != S(0, 10, 3) and S(0, 1) != S(1, 2)
    assert hash(S(0, 3, 5)) == hash(S(0, 1)) and hash(S(0, 0)) == hash(S(9, 2))
    assert len({S(0, 10, 2), S(0, 9, 2), S(1, 1)}) == 2


def test_list_rung_agrees(m):
    assert 9 in m.ListSpan(0, 10, 3) and len(m.ListSpan(0, 10, 3)) == 4
