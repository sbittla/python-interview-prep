import warnings

import pytest


def test_examples(load):
    m = load("ex01_diagnostic_bank")
    assert m.run_snippet("print(7 // -2, -7 % 3)") == "-4 2"
    assert m.grade({1: "-4 2"}, {29: 4, 30: 0})["total"] == 5


def test_bank_shape(load):
    m = load("ex01_diagnostic_bank")
    ids = sorted([*m.PREDICT, *m.CHOICE, *m.CODING])
    assert ids == list(range(1, 31))
    assert sum(m.MAX_POINTS.values()) == 36
    assert all(letter in m.COMPLEXITY_OPTIONS for _, letter in m.CHOICE.values())


def test_snippets_are_clean_and_deterministic(load):
    m = load("ex01_diagnostic_bank")
    with warnings.catch_warnings():
        warnings.simplefilter("error")          # a SyntaxWarning in a snippet fails here
        first = m.answer_key()
    assert m.answer_key() == first             # fresh namespace: no state leaks between runs
    assert all(first[q] for q in m.PREDICT)     # every snippet prints something
    assert "0x" not in "".join(first.values())  # no memory addresses


@pytest.mark.parametrize("qid, expected", [
    (2, "2 4"), (9, "[1, 2]"), (10, "[[1, 0], [1, 0]]"), (11, "[2, 2, 2]"),
    (13, "5 0"), (14, "TypeError (1, [2, 3])"), (15, "UnboundLocalError"),
])
def test_known_traps(load, qid, expected):
    m = load("ex01_diagnostic_bank")
    assert m.answer_key()[qid] == expected


def test_perfect_sheet_scores_36(load):
    m = load("ex01_diagnostic_bank")
    sheet = {q: f"  {a.lower()}  " if q in m.CHOICE else a for q, a in m.answer_key().items()}
    result = m.grade(sheet, {29: 4, 30: 4})
    assert result["total"] == 36 and result["missed"] == []


def test_empty_sheet_and_whitespace(load):
    m = load("ex01_diagnostic_bank")
    empty = m.grade({}, {})
    assert empty["total"] == 0 and empty["missed"] == list(range(1, 31))
    assert m.grade({8: "0   [1, 2, 3]\n4"}, {})["core"] == 1


def test_sample_sheet(load):
    m = load("ex01_diagnostic_bank")
    r = m.grade(m.SAMPLE_SHEET, m.SAMPLE_CODING)
    assert (r["core"], r["gotchas"], r["complexity"], r["coding"]) == (7, 4, 9, 6)
    assert r["missed"] == [2, 9, 11, 13, 14, 19, 27, 28, 30]


@pytest.mark.parametrize("points", [{29: 5}, {30: -1}])
def test_bad_coding_points(load, points):
    m = load("ex01_diagnostic_bank")
    with pytest.raises(ValueError):
        m.grade({}, points)
