import random

import pytest

M = "ex06_lcs_edit_distance"


def _is_subsequence(sub, s):
    it = iter(s)
    return all(ch in it for ch in sub)


def test_examples(load):
    m = load(M)
    assert (m.lcs("ABCBDAB", "BDCABA"), m.lcs_length("abc", "def")) == ("BCBA", 0)
    assert (m.edit_distance("horse", "ros"), m.edit_distance("", "abc")) == (3, 3)
    assert [op for op in m.edit_ops("cat", "cut") if op[0] != "keep"] == [("sub", "a", "u")]


@pytest.mark.parametrize("a, b, length", [
    ("", "", 0), ("", "abc", 0), ("abc", "abc", 3), ("abcde", "ace", 3), ("abc", "def", 0),
    ("aaaa", "aa", 2),
])
def test_lcs_edges(load, a, b, length):
    m = load(M)
    assert m.lcs_length(a, b) == m.lcs_length(b, a) == m.lcs_memo(a, b) == length
    assert m.lcs_table(a, b)[-1][-1] == length
    s = m.lcs(a, b)
    assert len(s) == length and _is_subsequence(s, a) and _is_subsequence(s, b)


@pytest.mark.parametrize("a, b, dist", [
    ("", "", 0), ("", "abc", 3), ("abc", "", 3), ("same", "same", 0), ("kitten", "sitting", 3),
    ("intention", "execution", 5), ("a", "b", 1), ("ab", "ba", 2),
])
def test_edit_edges(load, a, b, dist):
    m = load(M)
    assert m.edit_distance(a, b) == m.edit_distance(b, a) == m.edit_memo(a, b) == dist
    ops = m.edit_ops(a, b)
    assert m.apply_ops(a, ops) == b
    assert sum(op != "keep" for op, _, _ in ops) == dist


def test_random_against_brute(load):
    m = load(M)
    rng = random.Random(6)
    for _ in range(200):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        assert m.lcs_length(a, b) == m.lcs_brute(a, b) == len(m.lcs(a, b))
        d = m.edit_brute(a, b)
        assert m.edit_distance(a, b) == m.edit_table(a, b)[-1][-1] == d
        ops = m.edit_ops(a, b)
        assert m.apply_ops(a, ops) == b and sum(op != "keep" for op, _, _ in ops) == d


def test_insert_delete_only_identity(load):
    m = load(M)
    a, b = "sunday", "saturday"
    assert len(a) + len(b) - 2 * m.lcs_length(a, b) == 4
    assert m.edit_distance(a, b) == 3          # substitution makes it cheaper


def test_bad_script_rejected(load):
    m = load(M)
    with pytest.raises(AssertionError):
        m.apply_ops("abc", [("keep", "a", "a")])
