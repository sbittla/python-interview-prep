import pytest


def test_example_order(load):
    m = load("ex01_clarify_checklist")
    cats = [c for c, _ in m.checklist({"n": "int"})]
    assert cats == ["size", "output", "mutation", "range"]


def test_universal_questions_first_and_names_substituted(load):
    m = load("ex01_clarify_checklist")
    qs = m.checklist({"nums": "list[int]", "target": "int"})
    assert [c for c, _ in qs[:3]] == ["size", "output", "mutation"]
    assert any("nums" in q and c == "duplicates" for c, q in qs)
    assert any("target" in q for _, q in qs)
    assert all("{p}" not in q for _, q in qs)


def test_no_duplicate_texts(load):
    m = load("ex01_clarify_checklist")
    qs = m.checklist({"a": "list[int]", "b": "list[int]", "g": "graph"})
    texts = [q for _, q in qs]
    assert len(texts) == len(set(texts))
    # the same tag on two parameters still yields questions for both
    assert sum("Can a contain duplicates" in q for q in texts) == 1
    assert sum("Can b contain duplicates" in q for q in texts) == 1


def test_empty_spec_gives_universal_only(load):
    m = load("ex01_clarify_checklist")
    assert len(m.checklist({})) == 3


@pytest.mark.parametrize("spec, asked, missing", [
    ({"nums": "list[int]"}, {"size", "empty"},
     ["duplicates", "mutation", "output", "range", "sortedness"]),
    ({"s": "str"}, {"size", "output", "mutation", "empty", "types"}, []),
    ({"grid": "matrix[int]"}, set(), ["empty", "mutation", "output", "range", "shape", "size"]),
    ({"g": "graph"}, {"structure", "extra"}, ["empty", "mutation", "output", "size"]),
])
def test_audit(load, spec, asked, missing):
    m = load("ex01_clarify_checklist")
    assert m.audit(spec, asked) == missing


def test_unknown_tag(load):
    m = load("ex01_clarify_checklist")
    with pytest.raises(ValueError, match="tuple"):
        m.checklist({"x": "tuple"})


def test_deterministic(load):
    m = load("ex01_clarify_checklist")
    spec = {"words": "list[str]", "k": "int"}
    assert m.checklist(spec) == m.checklist(spec)
