import copy
import json

import pytest

OUTLINE = """### Chapter 7. Gotchas
7.1 Defaults
7.2 Copies
Not a section 7.3
### Chapter 16. Graphs
16.9 Union-find
16.10 Dijkstra
16.14–16.16 Reference algorithms
8.1 belongs to another chapter
## PART X
9.1 outside any chapter
16.20 after part break
"""

GOOD = {"id": "py01", "section": "44.1", "question": "Why is a default a bug?",
        "answer": "It is evaluated once. Use `None` and call `x.copy()` on 3.14 data.",
        "xref": "§7.1", "tags": ["references"], "keywords": ["once", "None"], "book": True}


@pytest.fixture
def m(load):
    return load("ex01_qa_bank_loader")


def test_parse_outline_rules(m):
    s = m.parse_outline(OUTLINE)
    assert s == {"7.1", "7.2", "16.9", "16.10", "16.14", "16.15", "16.16"}


def test_count_sentences_ignores_inner_dots(m):
    assert m.count_sentences("Calls `x.copy()` on 3.14 data.") == 1
    assert m.count_sentences("One. Two! Three? Four.") == 4
    assert m.count_sentences("") == 0


def test_good_entry_is_clean(m):
    assert m.validate([GOOD], m.parse_outline(OUTLINE)) == []


@pytest.mark.parametrize("change, fragment", [
    ({"id": "zz01"}, "bad id format"),
    ({"id": "py1"}, "bad id format"),
    ({"section": "44.2"}, "belongs in 44.1"),
    ({"question": "No question mark"}, "end with '?'"),
    ({"answer": "No full stop"}, "end with '.'"),
    ({"answer": "A. B. C. D."}, "4 sentences"),
    ({"answer": "once None " * 31 + "."}, "words"),
    ({"xref": "7.1"}, "bad xref format"),
    ({"xref": "§7.3"}, "not in COURSE_OUTLINE"),
    ({"xref": "§44.1"}, "chapter 44 itself"),
    ({"tags": []}, "tags"),
    ({"tags": ["Bad Tag"]}, "tags"),
    ({"keywords": []}, "0 keywords"),
    ({"keywords": ["zebra"]}, "'zebra' not in answer"),
    ({"book": "yes"}, "'book' must be a bool"),
    ({"tags": "references"}, "'tags' must be a list"),
    ({"answer": 3}, "non-string 'answer'"),
])
def test_each_rule_fires(m, change, fragment):
    e = dict(GOOD, **change)
    errs = m.validate([e], m.parse_outline(OUTLINE))
    assert any(fragment in err for err in errs), errs


def test_duplicates_and_all_errors_reported(m):
    other = dict(GOOD, question="WHY IS A DEFAULT A BUG?")
    errs = m.validate([GOOD, other, {"question": "x?"}], m.parse_outline(OUTLINE))
    assert sum("duplicate id" in e for e in errs) == 2
    assert sum("duplicate question" in e for e in errs) == 2
    assert any(e.startswith("#2:") for e in errs)


def test_missing_ids_are_not_duplicates(m):
    errs = m.validate([{"question": "a?"}, {"question": "b?"}], m.parse_outline(OUTLINE))
    assert not any("duplicate" in e for e in errs), errs
    assert sum("non-string 'id'" in e for e in errs) == 2
    errs = m.validate([dict(GOOD, question=None), dict(GOOD, id="py02", question=None)],
                      m.parse_outline(OUTLINE))
    assert not any("duplicate question" in e for e in errs), errs


def test_unhashable_id_does_not_crash(m):
    errs = m.validate([dict(GOOD, id=["x"]), dict(GOOD, id=["x"], question="Other?")],
                      m.parse_outline(OUTLINE))
    assert sum("non-string 'id'" in e for e in errs) == 2
    assert not any("duplicate id" in e for e in errs)
    assert errs[0].startswith("#0:")


def test_load_bank_rejects_non_list(m, tmp_path):
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"id": "py01"}), encoding="utf-8")
    with pytest.raises(ValueError):
        m.load_bank(p)


def test_real_bank_is_valid_against_real_outline(m):
    bank = m.load_bank(m.BANK_PATH)
    sections = m.parse_outline(m.OUTLINE_PATH.read_text(encoding="utf-8"))
    assert "16.10" in sections and "44.7" in sections and "7.28" in sections
    assert m.validate(bank, sections) == []
    per = {}
    for e in bank:
        per.setdefault(e["section"], [0, 0])
        per[e["section"]][0] += 1
        per[e["section"]][1] += e.get("book", False)
    assert sorted(per) == sorted(m.PREFIX_SECTION.values())
    assert all(total >= 10 and 8 <= book <= 14 for total, book in per.values())


def test_validate_does_not_mutate(m):
    e = copy.deepcopy(GOOD)
    m.validate([e], m.parse_outline(OUTLINE))
    assert e == GOOD
