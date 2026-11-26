from fractions import Fraction

import pytest

GOOD = {"clarifying": 4, "approach": 3, "correctness": 3, "code_quality": 3,
        "complexity": 2, "testing": 2, "communication": 4}


def test_weights_match_outline(load):
    m = load("ex01_rubric_scorer")
    assert [(label, w) for _, label, w in m.CODING_RUBRIC] == [
        ("Clarifying requirements and constraints", 10),
        ("Approach and trade-off reasoning", 20),
        ("Correctness on tests and edge cases", 25),
        ("Code quality and Pythonic style", 15),
        ("Complexity analysis", 10),
        ("Testing and debugging", 10),
        ("Communication", 10)]
    assert [(label, w) for _, label, w in m.AI_RUBRIC] == [
        ("Problem decomposition and planning", 20),
        ("Prompting and context management", 15),
        ("Verifying and critiquing AI output", 30),
        ("Integration and code quality", 20),
        ("Explaining and owning the final code", 15)]


def test_worked_example(load):
    m = load("ex01_rubric_scorer")
    card = m.score(m.CODING_RUBRIC, GOOD)
    assert card.total == Fraction(75)
    assert card.verdict == "close"
    assert [r.points for r in card.rows] == [10, 15, Fraction(75, 4), Fraction(45, 4), 5, 5, 10]
    assert [f.split(":")[0] for f in card.feedback] == [
        "Correctness on tests and edge cases", "Approach and trade-off reasoning",
        "Complexity analysis"]
    assert "-6.25" in card.feedback[0]


@pytest.mark.parametrize("rating, total, verdict", [
    (4, 100, "ready"), (0, 0, "not yet"), (2, 50, "not yet"), (3, 75, "close")])
def test_uniform_ratings(load, rating, total, verdict):
    m = load("ex01_rubric_scorer")
    card = m.score(m.CODING_RUBRIC, {k: rating for k, _, _ in m.CODING_RUBRIC})
    assert card.total == total and card.verdict == verdict
    if rating == 4:
        assert card.feedback == ()


def test_band_boundaries(load):
    m = load("ex01_rubric_scorer")
    # 85 exactly with every rating >= 2
    r = {"clarifying": 3, "approach": 4, "correctness": 4, "code_quality": 4,
         "complexity": 2, "testing": 3, "communication": 2}
    card = m.score(m.CODING_RUBRIC, r)
    assert card.total == 85 and card.verdict == "ready"
    # 70 exactly -> close; 68.75 -> not yet
    r70 = {"clarifying": 2, "approach": 3, "correctness": 3, "code_quality": 3,
           "complexity": 3, "testing": 3, "communication": 2}
    card = m.score(m.CODING_RUBRIC, r70)
    assert card.total == 70 and card.verdict == "close"
    below = {**r70, "clarifying": 3, "code_quality": 2}
    card = m.score(m.CODING_RUBRIC, below)
    assert card.total == Fraction(275, 4) and card.verdict == "not yet"
    # 83.75 is close, not ready
    card = m.score(m.CODING_RUBRIC, {**r, "code_quality": 3, "clarifying": 4})
    assert card.total == Fraction(335, 4) and card.verdict == "close"


def test_floor_rule(load):
    m = load("ex01_rubric_scorer")
    r = {k: 4 for k, _, _ in m.CODING_RUBRIC}
    r["testing"] = 1
    card = m.score(m.CODING_RUBRIC, r)
    assert card.total == Fraction(185, 2)
    assert card.verdict.startswith("close") and "Testing and debugging" in card.verdict
    r["testing"] = 2
    assert m.score(m.CODING_RUBRIC, r).verdict == "ready"


def test_feedback_tie_and_skip_zero(load):
    m = load("ex01_rubric_scorer")
    r = {k: 4 for k, _, _ in m.CODING_RUBRIC}
    r["communication"] = 3   # loses 2.5
    r["clarifying"] = 3      # loses 2.5, earlier in rubric order
    card = m.score(m.CODING_RUBRIC, r)
    assert [f.split(":")[0] for f in card.feedback] == [
        "Clarifying requirements and constraints", "Communication"]


def test_ai_rubric(load):
    m = load("ex01_rubric_scorer")
    card = m.score(m.AI_RUBRIC, {"decomposition": 3, "prompting": 3, "verifying": 2,
                                 "integration": 3, "ownership": 2})
    assert card.total == Fraction(255, 4) and card.verdict == "not yet"
    assert card.feedback[0].startswith("Verifying and critiquing AI output: -15.00")


@pytest.mark.parametrize("change", [
    {"complexty": 3}, {"testing": 5}, {"testing": -1}, {"testing": True},
    {"testing": 2.0}, {"testing": "3"}])
def test_bad_ratings(load, change):
    m = load("ex01_rubric_scorer")
    with pytest.raises(ValueError):
        m.score(m.CODING_RUBRIC, {**GOOD, **change})


def test_missing_key_named(load):
    m = load("ex01_rubric_scorer")
    r = dict(GOOD)
    del r["testing"]
    with pytest.raises(ValueError, match="testing"):
        m.score(m.CODING_RUBRIC, r)


@pytest.mark.parametrize("rubric", [
    (("a", "A", 50), ("b", "B", 49)),
    (("a", "A", 50), ("a", "B", 50)),
    (("a", "A", 100), ("b", "B", 0)),
    (("a", "A", 50.0), ("b", "B", 50)),
])
def test_bad_rubric(load, rubric):
    m = load("ex01_rubric_scorer")
    with pytest.raises(ValueError):
        m.validate_rubric(rubric)
