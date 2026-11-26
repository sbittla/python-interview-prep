import json
import sys

import pytest


@pytest.fixture
def m(load):
    return load("ex04_predict_output")


def _items(m):
    return json.loads(m.DATA_PATH.read_text(encoding="utf-8"))


def test_every_snippet_matches_real_execution(m):
    items = _items(m)
    assert len(items) >= 15
    for it in items:                 # executed now, so the key cannot drift from Python
        assert m.run_snippet(it["code"]) == it["expected"], it["id"]


def test_bank_shape(m):
    items = _items(m)
    assert len({it["id"] for it in items}) == len(items)
    assert all(it["xref"].startswith("§7.") or it["xref"] in ("§5.8", "§6.12")
               for it in items)
    sets = {it["set"] for it in items}
    assert len(sets) >= 5
    assert any("raises" in it["expected"] for it in items)


def test_check_reports_mismatch(m):
    items = [{"id": "x", "code": "print(1 + 1)", "expected": "3\n"},
             {"id": "y", "code": "print(2)", "expected": "2\n"}]
    assert m.check(items) == [("x", "3\n", "2\n")]


@pytest.mark.parametrize("code, out", [
    ("print(-7 // 2)", "-4\n"),
    ("[][0]", "raises IndexError\n"),
    ("print('a')\n{}['k']", "a\nraises KeyError\n"),
    ("x = 1", ""),
])
def test_run_snippet(m, code, out):
    assert m.run_snippet(code) == out


def test_namespace_isolated_and_stdout_restored(m):
    before = sys.stdout
    m.run_snippet("leak = 42\nraise ValueError")
    assert sys.stdout is before
    assert m.run_snippet("print(leak)") == "raises NameError\n"
    assert m.run_snippet("print(__name__)") == "__snippet__\n"


def test_base_exceptions_not_swallowed(m):
    with pytest.raises(SystemExit):
        m.run_snippet("raise SystemExit(3)")


def test_quiz_sheet_hides_answers(m):
    items = _items(m)
    sheet = m.quiz_sheet(items, "numbers")
    numbers = [it for it in items if it["set"] == "numbers"]
    assert numbers
    for it in numbers:
        assert f"[{it['id']}] {it['xref']}" in sheet and it["code"] in sheet
    assert "-4 1 2 4" not in sheet
    assert m.quiz_sheet(items, "no-such-set") == ""
