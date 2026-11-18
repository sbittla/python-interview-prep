import pytest


def test_examples(load):
    m = load("ex08_palindrome_partitioning")
    assert m.solve("aab") == [["a", "a", "b"], ["aa", "b"]]
    assert m.solve("a") == [["a"]]


@pytest.mark.parametrize("s", ["abba", "racecar", "aabbaa", "abc"])
def test_matches_brute_force(load, s):
    m = load("ex08_palindrome_partitioning")
    got = m.solve(s)
    assert sorted(got) == sorted(m.brute_force(s))
    assert all("".join(p) == s and all(x == x[::-1] for x in p) for p in got)


def test_all_same_letter(load):
    m = load("ex08_palindrome_partitioning")
    assert len(m.solve("a" * 10)) == 2 ** 9
