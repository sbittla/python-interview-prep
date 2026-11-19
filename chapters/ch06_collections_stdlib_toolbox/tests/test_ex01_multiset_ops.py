import random
from collections import Counter

import pytest


def test_examples(load):
    m = load("ex01_multiset_ops")
    assert m.can_spell("noon", "on no") is True
    assert m.shortfall("banana", "ban") == {"a": 2, "n": 1}
    assert m.shared_stickers("aabbc", "abbbd") == "abb"
    assert m.combined_need(["moon", "mono", "nom"]) == "mnoo"


@pytest.mark.parametrize("word, sheet, ok, missing", [
    ("", "", True, {}),
    ("a", "", False, {"a": 1}),
    ("aa", "a", False, {"a": 1}),
    ("a b", "ba", True, {}),
    ("zzz", "zzzz", True, {}),
])
def test_edge_cases(load, word, sheet, ok, missing):
    m = load("ex01_multiset_ops")
    assert m.can_spell(word, sheet) is ok
    assert m.brute_force_can_spell(word, sheet) is ok
    assert m.shortfall(word, sheet) == missing


def test_empty_inputs(load):
    m = load("ex01_multiset_ops")
    assert m.shared_stickers("", "abc") == ""
    assert m.combined_need([]) == ""


def test_random_against_brute(load):
    m = load("ex01_multiset_ops")
    rng = random.Random(1)
    for _ in range(300):
        w = "".join(rng.choice("abc ") for _ in range(rng.randint(0, 6)))
        s = "".join(rng.choice("abc ") for _ in range(rng.randint(0, 8)))
        assert m.can_spell(w, s) == m.brute_force_can_spell(w, s)
        assert (m.shortfall(w, s) == {}) == m.can_spell(w, s)
        inter = m.shared_stickers(w, s)
        assert Counter(inter) == Counter(w.replace(" ", "")) & Counter(s.replace(" ", ""))
