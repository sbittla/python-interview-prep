import random

import pytest


def test_examples(load):
    m = load("ex07_group_anagrams")
    expected = [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
    assert m.solve(["eat", "tea", "tan", "ate", "nat", "bat"]) == expected


@pytest.mark.parametrize("words, expected", [
    ([], []), ([""], [[""]]), (["", "", "a"], [["", ""], ["a"]]), (["ab", "ba", "ab"], [["ab", "ab", "ba"]]),
])
def test_edge_cases(load, words, expected):
    assert load("ex07_group_anagrams").solve(words) == expected


def test_count_key(load):
    m = load("ex07_group_anagrams")
    assert m.count_key("abca")[:3] == (2, 1, 1)
    assert len(m.count_key("")) == 26


def test_random_methods_agree(load):
    m = load("ex07_group_anagrams")
    rng = random.Random(7)
    for _ in range(100):
        words = ["".join(rng.choice("abc") for _ in range(rng.randint(0, 3))) for _ in range(rng.randint(0, 8))]
        assert m.solve(words) == m.by_sorted_key(words) == m.brute_force(words)
