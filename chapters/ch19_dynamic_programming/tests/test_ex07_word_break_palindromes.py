import random

import pytest

M = "ex07_word_break_palindromes"
WORDS = {"cats", "dog", "sand", "and", "cat"}


def test_examples(load):
    m = load(M)
    assert m.word_break("applepenapple", {"apple", "pen"}) is True
    assert m.word_break("catsandog", WORDS) is False
    assert m.word_break_split("pineapplepen", {"apple", "pen", "pine", "pineapple"}) == ["pineapple", "pen"]
    assert (m.count_pal_substrings("aaa"), m.lps("bbbab"), m.lps("cbbd")) == (6, 4, 2)


@pytest.mark.parametrize("s, ok", [
    ("", True), ("catsanddog", True), ("catsandog", False), ("dogcat", True), ("do", False),
])
def test_word_break_edges(load, s, ok):
    m = load(M)
    assert m.word_break(s, WORDS) == m.word_break_memo(s, WORDS) == m.word_break_brute(s, WORDS) == ok
    split = m.word_break_split(s, WORDS)
    if ok:
        assert "".join(split) == s and all(w in WORDS for w in split)
    else:
        assert split is None


def test_word_break_adversarial_input_is_fast(load):
    m = load(M)
    assert m.word_break("a" * 1000 + "b", {"a", "aa", "aaa"}) is False
    assert m.word_break_split("a" * 1000, {"a", "aa", "aaa"}) is not None


def test_word_break_random(load):
    m = load(M)
    rng = random.Random(17)
    for _ in range(200):
        words = {"".join(rng.choice("ab") for _ in range(rng.randint(1, 3))) for _ in range(3)}
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 10)))
        expected = m.word_break_brute(s, words)
        assert m.word_break(s, words) == m.word_break_memo(s, words) == expected
        split = m.word_break_split(s, words)
        assert (split is not None) == expected
        if split is not None:
            assert "".join(split) == s and all(w in words for w in split)


@pytest.mark.parametrize("s, count", [
    ("", 0), ("a", 1), ("ab", 2), ("aaa", 6), ("abba", 6), ("racecar", 10),
])
def test_pal_substrings(load, s, count):
    m = load(M)
    assert m.count_pal_substrings(s) == m.count_pal_substrings_table(s) == count
    assert m.count_pal_substrings_brute(s) == count


@pytest.mark.parametrize("s, length", [
    ("", 0), ("a", 1), ("ab", 1), ("bbbab", 4), ("cbbd", 2), ("character", 5), ("racecar", 7),
])
def test_lps(load, s, length):
    m = load(M)
    assert m.lps(s) == m.lps_table(s) == m.lps_memo(s) == length


def test_random_palindromes(load):
    m = load(M)
    rng = random.Random(23)
    for _ in range(200):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 10)))
        assert m.count_pal_substrings(s) == m.count_pal_substrings_table(s) == m.count_pal_substrings_brute(s)
        assert m.lps(s) == m.lps_table(s) == m.lps_brute(s)
