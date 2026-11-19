import random

import pytest

NAME = "ex08_permutation_in_string"


def test_examples(load):
    m = load(NAME)
    assert (m.solve("ab", "eidbaooo"), m.solve("ab", "eidboaoo")) == (True, False)
    assert m.anagram_starts("abc", "cbaebabacd") == [0, 6]


@pytest.mark.parametrize("p, s, expected", [
    ("a", "", []), ("abc", "ab", []), ("aa", "aaaa", [0, 1, 2]), ("aab", "abbab", []),
    ("ab", "ab", [0]), ("xyz", "zyx..xzy", [0, 5]),
])
def test_edge_cases(load, p, s, expected):
    assert load(NAME).anagram_starts(p, s) == expected


def test_random_all_rungs_agree(load):
    m = load(NAME)
    rng = random.Random(1008)
    for _ in range(400):
        p = "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 14)))
        starts = m.anagram_starts(p, s)
        assert starts == m.anagram_starts_brute(p, s)
        assert m.solve(p, s) == m.brute_force(p, s) == m.sorted_windows(p, s) == bool(starts)


def test_set_compare_ignores_counts(load):
    m = load(NAME)
    assert m.wrong_set_compare("aab", "abbab") is True
    assert m.solve("aab", "abbab") is False
