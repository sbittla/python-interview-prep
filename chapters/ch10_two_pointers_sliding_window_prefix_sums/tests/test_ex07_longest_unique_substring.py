import random

import pytest

NAME = "ex07_longest_unique_substring"


def test_examples(load):
    m = load(NAME)
    assert (m.solve("abcabcbb"), m.best_substring("abcabcbb")) == (3, "abc")
    assert (m.solve("pwwkew"), m.best_substring("pwwkew")) == (3, "wke")


@pytest.mark.parametrize("s, expected", [
    ("", 0), ("a", 1), ("bbbbb", 1), ("abba", 2), ("dvdf", 3), ("tmmzuxt", 5), (" ", 1),
    ("aé€a", 3),
])
def test_edge_cases(load, s, expected):
    assert load(NAME).solve(s) == expected


def test_random_all_rungs_agree(load):
    m = load(NAME)
    rng = random.Random(1007)
    for _ in range(400):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 14)))
        want = m.brute_force(s)
        assert m.solve(s) == m.extend_each_start(s) == m.last_index_jump(s) == want
        best = m.best_substring(s)
        assert len(best) == want and len(set(best)) == len(best) and best in s


def test_jump_without_max_is_wrong(load):
    assert load(NAME).wrong_jump_without_max("abba") == 3
