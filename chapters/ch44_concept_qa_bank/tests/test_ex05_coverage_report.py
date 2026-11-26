import json

import pytest

BANK = [
    {"section": "44.1", "xref": "§7.1", "tags": ["a"], "book": True},
    {"section": "44.1", "xref": "§16.10", "tags": ["a", "b"]},
    {"section": "44.3", "xref": "§16.9", "tags": ["c", "b"], "book": False},
    {"section": "44.3", "xref": "§7.2", "tags": ["a"], "book": True},
]


@pytest.fixture
def m(load):
    return load("ex05_coverage_report")


def test_section_counts(m):
    assert m.section_counts(BANK) == {"44.1": (2, 1), "44.3": (2, 1)}
    assert m.section_counts([]) == {}


def test_chapter_refs_numeric_order(m):
    assert list(m.chapter_refs(BANK).items()) == [(7, 2), (16, 2)]
    bank = [{"xref": "§16.10"}, {"xref": "§9.4"}, {"xref": "§7.1"}, {"xref": "§16.2"}]
    assert list(m.chapter_refs(bank)) == [7, 9, 16]        # as strings: "16" < "7" < "9"
    assert m.chapter_refs(bank)[16] == 2


def test_top_tags_ties_alphabetical(m):
    assert m.top_tags(BANK, 2) == [("a", 3), ("b", 2)]
    assert m.top_tags(BANK, 10) == [("a", 3), ("b", 2), ("c", 1)]
    bank = [{"tags": ["z"]}, {"tags": ["m"]}, {"tags": ["q", "z"]}, {"tags": ["m"]}]
    assert m.top_tags(bank, 3) == [("m", 2), ("z", 2), ("q", 1)]   # z arrived first


def test_gaps_include_empty_sections(m):
    assert m.gaps(BANK, ["44.1", "44.2", "44.3"], 2, 1) == [("44.2", 0, 0)]
    assert m.gaps(BANK, ["44.1", "44.3"], 2, 2) == [("44.1", 2, 1), ("44.3", 2, 1)]


def test_uncited(m):
    assert m.uncited(BANK, [5, 7, 16, 21]) == [5, 21]


def test_real_bank_covers_course(m):
    bank = json.loads(m.BANK_PATH.read_text(encoding="utf-8"))
    assert m.gaps(bank, m.SECTIONS, 10, 8) == []
    assert m.uncited(bank, list(range(5, 44))) == []
