import pytest


def test_strong_hire(load):
    m = load("ex05_signal_scorer")
    r = m.score_round("coding", {"problem_solving": 4, "coding": 4, "communication": 3, "testing": 3})
    assert r == {"score": 3.65, "decision": "strong hire", "weakest": "testing"}


def test_veto(load):
    m = load("ex05_signal_scorer")
    r = m.score_round("coding", {"problem_solving": 4, "coding": 1, "communication": 4, "testing": 4})
    assert r["decision"] == "no hire" and r["score"] == 3.1 and r["weakest"] == "coding"


def test_low_weight_one_is_not_veto(load):
    m = load("ex05_signal_scorer")
    r = m.score_round("coding", {"problem_solving": 4, "coding": 4, "communication": 1, "testing": 4})
    assert r["decision"] == "strong hire"
    assert r["weakest"] == "communication"


def test_tie_break_by_weight(load):
    m = load("ex05_signal_scorer")
    r = m.score_round("ml_coding", {"problem_solving": 3, "coding": 3, "communication": 3,
                                    "testing": 2, "domain": 2})
    assert r["weakest"] == "domain"


@pytest.mark.parametrize("ratings", [
    {"coding": 3},
    {"problem_solving": 5, "coding": 3, "communication": 3, "testing": 3},
])
def test_errors(load, ratings):
    m = load("ex05_signal_scorer")
    with pytest.raises(ValueError):
        m.score_round("coding", ratings)
