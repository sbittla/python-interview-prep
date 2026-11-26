import random

import pytest

REF = "Rotate access keys every 90 days."
GOOD, BAD = "Rotate access keys every 90 days.", "Keys never need rotation."


def test_examples(load):
    m = load("ex10_llm_judge")
    assert m.cohen_kappa(["A", "A", "B", "B"], ["A", "B", "B", "B"]) == 0.5


def test_kappa_cases(load):
    m = load("ex10_llm_judge")
    assert m.cohen_kappa(["A"] * 9 + ["B"], ["A"] * 10) == 0.0      # 90% agreement, chance level
    assert m.cohen_kappa(["A", "B"], ["B", "A"]) == -1.0
    assert m.cohen_kappa(["A", "A"], ["A", "A"]) == 1.0                # p_e == 1
    with pytest.raises(ValueError):
        m.cohen_kappa([], [])
    with pytest.raises(ValueError):
        m.cohen_kappa(["A"], ["A", "B"])


def test_kappa_random_against_formula(load):
    m = load("ex10_llm_judge")
    rng = random.Random(410)
    for _ in range(100):
        n = rng.randint(1, 20)
        x = [rng.choice("ABC") for _ in range(n)]
        y = [rng.choice("ABC") for _ in range(n)]
        po = sum(a == b for a, b in zip(x, y)) / n
        pe = sum((x.count(c) / n) * (y.count(c) / n) for c in "ABC")
        expected = 1.0 if pe == 1 else round((po - pe) / (1 - pe), 4)
        assert m.cohen_kappa(x, y) == pytest.approx(expected)


def test_quality_and_unbiased_judge(load):
    m = load("ex10_llm_judge")
    j = m.MockJudge()
    assert j.quality(REF, GOOD) == 1.0 and j.quality(REF, BAD) == pytest.approx(1 / 6)
    assert j.quality("", GOOD) == 0.0
    assert j.compare(REF, GOOD, BAD) == "A" and j.compare(REF, BAD, GOOD) == "B"
    assert j.compare(REF, GOOD, GOOD) == "A"                          # tie goes to the first slot


def test_swap_verdict(load):
    m = load("ex10_llm_judge")
    assert m.swap_verdict(m.MockJudge(), REF, BAD, GOOD) == "B"
    assert m.swap_verdict(m.MockJudge(), REF, GOOD, GOOD) == "inconsistent"   # tie -> order decides
    biased = m.MockJudge(position_bias=0.9)
    assert biased.compare(REF, BAD, GOOD) == "A"
    assert m.swap_verdict(biased, REF, BAD, GOOD) == "inconsistent"
    j = m.MockJudge()
    m.swap_verdict(j, REF, GOOD, BAD)
    assert j.calls == 2


def test_reports_on_data(load):
    m = load("ex10_llm_judge")
    pairs = m.load_pairs()
    assert m.judge_report(m.MockJudge(), pairs, swap=False) == {
        "accuracy": 1.0, "coverage": 1.0, "flip_rate": 0.0}
    pos = m.MockJudge(position_bias=0.3)
    assert m.judge_report(pos, pairs, swap=False) == {"accuracy": 0.9, "coverage": 1.0, "flip_rate": 0.4}
    assert m.judge_report(pos, pairs, swap=True) == {"accuracy": 1.0, "coverage": 0.6, "flip_rate": 0.4}
    length = m.MockJudge(length_bias=0.02)
    rep = m.judge_report(length, pairs, swap=True)
    assert rep["flip_rate"] == 0.0 and rep["accuracy"] == 0.8      # swapping does not fix length bias


def test_report_empty(load):
    m = load("ex10_llm_judge")
    assert m.judge_report(m.MockJudge(), [], swap=True) == {"accuracy": 0.0, "coverage": 0.0, "flip_rate": 0.0}
