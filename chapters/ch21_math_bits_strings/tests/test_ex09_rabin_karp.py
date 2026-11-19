import random

import pytest


def _count_occurrences(s, sub):
    return sum(s.startswith(sub, i) for i in range(len(s)))


def test_examples(load):
    m = load("ex09_rabin_karp")
    assert m.rk_search("abracadabra", "abra") == [0, 7]
    assert m.longest_dup_substring("banana") == "ana"


@pytest.mark.parametrize("text, pat, expected", [
    ("", "", [0]), ("abc", "", [0, 1, 2, 3]), ("ab", "abc", []), ("aaaa", "aa", [0, 1, 2]),
])
def test_edge_cases(load, text, pat, expected):
    assert load("ex09_rabin_karp").rk_search(text, pat) == expected


def test_tiny_modulus_still_correct(load):
    m = load("ex09_rabin_karp")
    rng = random.Random(12)
    total_spurious = 0
    for _ in range(200):
        text = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 60)))
        pat = "".join(rng.choice("abcd") for _ in range(rng.randint(1, 5)))
        expected = [i for i in range(len(text) - len(pat) + 1) if text.startswith(pat, i)]
        hits, spurious = m.rk_search_stats(text, pat, mod=7, base=3)
        assert hits == expected == m.rk_search(text, pat)
        total_spurious += spurious
    assert total_spurious > 0          # collisions did happen; verification rejected them


def test_longest_dup_random(load):
    m = load("ex09_rabin_karp")
    rng = random.Random(13)
    for _ in range(200):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 30)))
        brute = m.longest_dup_brute(s)
        for got in (m.longest_dup_substring(s), m.longest_dup_slices(s)):
            assert len(got) == len(brute)
            if got:
                assert _count_occurrences(s, got) >= 2


def test_longest_dup_known(load):
    m = load("ex09_rabin_karp")
    assert m.longest_dup_substring("abcd") == ""
    assert m.longest_dup_substring("aaaaa") == "aaaa"
    assert m.longest_dup_substring("a") == ""
