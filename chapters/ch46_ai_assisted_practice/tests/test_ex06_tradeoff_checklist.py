import re

import pytest

M = "ex06_tradeoff_checklist"
ALL = ["complexity", "space", "alternative", "edge cases", "assumptions", "evidence"]


def test_vague_answer_misses_everything(load):
    r = load(M).score("It is faster and cleaner now.")
    assert r.hits == [] and r.missing == ALL and r.ok is False and r.words == 6


@pytest.mark.parametrize("text, item", [
    ("runs in O(n log n)", "complexity"),
    ("it is LINEAR", "complexity"),
    ("uses more memory", "space"),
    ("a heap vs a sort", "alternative"),
    ("rather than sorting", "alternative"),
    ("the empty list", "edge cases"),
    ("it assumes sorted input", "assumptions"),
    ("requires hashable keys", "assumptions"),
    ("my tests cover it", "evidence"),
    ("checked against an oracle", "evidence"),
])
def test_items_are_recognised(load, text, item):
    assert item in load(M).score(text).hits


@pytest.mark.parametrize("text, item", [
    ("the contest", "evidence"),
    ("the devs", "alternative"),
    ("the knowledge graph", "edge cases"),
    ("spacecraft", "space"),
    ("Ohio(n) state", "complexity"),
])
def test_word_boundaries_prevent_false_hits(load, text, item):
    assert item not in load(M).score(text).hits


def test_hits_and_missing_keep_checklist_order(load):
    r = load(M).score("tests show it breaks on empty input; O(1) space")
    assert r.hits == ["complexity", "space", "edge cases", "assumptions", "evidence"]
    assert r.missing == ["alternative"]


def test_word_budget(load):
    m = load(M)
    full = ("O(n) time, O(1) space, instead of sorting; empty input handled; "
            "assumes ints; tests pass.")
    assert m.score(full).ok
    assert not m.score(full + " padding" * 200).ok
    assert m.score(full, max_words=5).ok is False
    exact = full + " ok" * (m.MAX_WORDS - len(full.split()))        # exactly MAX_WORDS words
    assert m.score(exact).words == m.MAX_WORDS and m.score(exact).ok


def test_keyword_soup_is_the_documented_limit(load):
    m = load(M)
    assert m.score("O(n) O(n^2) hashable space vs empty requires test").ok   # mentions only


def test_custom_checklist(load):
    m = load(M)
    r = m.score("we would cache it", checklist=(("caching", (r"\bcache\b",)),))
    assert r.hits == ["caching"] and r.missing == [] and r.ok


def test_my_explanation_passes_and_is_specific(load):
    m = load(M)
    r = m.score(m.MY_EXPLANATION)
    assert r.ok, r.missing
    text = m.MY_EXPLANATION
    assert len(text.split()) >= 40                                    # an answer, not keywords
    assert len(re.findall(r"[.!?](\s|$)", text)) >= 4                 # several sentences
    assert re.search(r"O\(n\)", text)
    assert re.search(r"O\(n(\^2|²|\*\*2|\s*\*\s*n)\)", text)
    assert re.search(r"\bhashable\b", text, re.I)
