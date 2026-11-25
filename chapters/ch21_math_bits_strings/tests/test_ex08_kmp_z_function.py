import random

import pytest


def test_examples(load):
    m = load("ex08_kmp_z_function")
    assert m.prefix_function("aabaaab") == [0, 1, 0, 1, 2, 2, 3]
    assert m.kmp_search("abababa", "aba") == [0, 2, 4]
    assert (m.smallest_repeating_unit("abcabcabc"), m.smallest_repeating_unit("abcab")) == (3, 5)
    assert len("abcab") - m.prefix_function("abcab")[-1] == 3     # shortest period, not a unit
    assert m.z_function("aabxaab") == [7, 1, 0, 0, 3, 1, 0]


@pytest.mark.parametrize("text, pat, expected", [
    ("", "", [0]), ("abc", "", [0, 1, 2, 3]), ("", "a", []), ("ab", "abc", []),
    ("aaaaa", "aa", [0, 1, 2, 3]), ("abc", "abc", [0]),
])
def test_edge_cases(load, text, pat, expected):
    m = load("ex08_kmp_z_function")
    assert m.kmp_search(text, pat) == m.z_search(text, pat) == m.find_all(text, pat) == expected


def _brute_pi(s):
    return [max(k for k in range(i + 1) if s[:k] == s[i + 1 - k:i + 1]) for i in range(len(s))]


def _brute_z(s):
    z = []
    for i in range(len(s)):
        k = 0
        while i + k < len(s) and s[k] == s[i + k]:
            k += 1
        z.append(k)
    return z


def test_random_against_find_and_brute(load):
    m = load("ex08_kmp_z_function")
    rng = random.Random(10)
    for _ in range(500):
        text = "".join(rng.choice("ab") for _ in range(rng.randint(0, 40)))
        pat = "".join(rng.choice("ab") for _ in range(rng.randint(0, 5)))
        expected = m.find_all(text, pat)
        assert m.kmp_search(text, pat) == m.z_search(text, pat) == expected
        if pat:
            assert m.brute_search(text, pat) == expected
        assert m.prefix_function(text) == _brute_pi(text)
        assert m.z_function(text) == _brute_z(text)


def test_smallest_repeating_unit(load):
    m = load("ex08_kmp_z_function")
    rng = random.Random(11)
    for _ in range(300):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 12)))
        expected = next(p for p in range(1, len(s) + 1) if len(s) % p == 0 and s[:p] * (len(s) // p) == s)
        assert m.smallest_repeating_unit(s) == expected
