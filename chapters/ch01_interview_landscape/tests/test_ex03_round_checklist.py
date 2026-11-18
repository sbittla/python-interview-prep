import pytest


def test_common_first(load):
    m = load("ex03_round_checklist")
    items = m.build_checklist(["online_judge"], "ai_free")
    assert items[: len(m.COMMON)] == m.COMMON
    assert items[0] == "Confirm the language and Python version you will use"


def test_dedup_and_order(load):
    m = load("ex03_round_checklist")
    items = m.build_checklist(["Shared_Editor", "whiteboard", "shared_editor"], "ai_free")
    assert len(items) == len(set(items))
    dry = "Dry-run on a small example by tracing variables in a table"
    assert items.count(dry) == 1
    assert items.index("Practise in a plain editor without autocomplete or linting") < items.index(
        "Practise writing code by hand without autocomplete")
    assert items[-1].startswith("Memorise stdlib")


@pytest.mark.parametrize("formats, policy", [(["hackathon"], "ai_free"), (["take_home"], "maybe")])
def test_invalid(load, formats, policy):
    m = load("ex03_round_checklist")
    with pytest.raises(ValueError):
        m.build_checklist(formats, policy)


def test_render(load):
    m = load("ex03_round_checklist")
    assert m.render(["a", "b"]) == " 1. [ ] a\n 2. [ ] b"
    assert m.render([]) == ""
