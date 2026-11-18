import pytest


def test_standard_plan_matches_outline(load):
    m = load("ex01_study_plan")
    weeks = m.build_plan("8-week", "S")
    assert [w.week for w in weeks] == list(range(1, 9))
    assert [w.problems for w in weeks] == [15, 18, 18, 18, 18, 10, 10, 12]
    assert m.total_problems(weeks) == 119
    assert weeks[0].chapters == list(range(1, 10))
    assert weeks[3].checkpoint == "Mock #1 (rubric-scored)"
    assert weeks[7].chapters == [44, 45, 46, 47, 48]


@pytest.mark.parametrize("track, wk6, wk7", [
    ("S", [29, 30], [28, 31, 32]),
    ("M", [33, 34, 35], [36, 37]),
    ("L", [38, 39, 40], [41, 42, 43]),
])
def test_track_weeks(load, track, wk6, wk7):
    weeks = load("ex01_study_plan").build_plan("8-week", track)
    assert weeks[5].chapters == wk6 and weeks[6].chapters == wk7
    assert weeks[5].labs and weeks[6].labs


def test_other_plans(load):
    m = load("ex01_study_plan")
    assert len(m.build_plan("4-week", "S")) == 4
    twelve = m.build_plan("12-week", "M")
    assert [w.week for w in twelve] == list(range(1, 13))
    assert twelve[4].chapters == list(range(1, 10))  # the 8-week plan starts at week 5
    six = m.build_plan("6-week", "L")
    assert len(six) == 6 and six[-1].chapters == [44, 46, 47, 48]
    assert m.checkpoints(six)[0].startswith("W1: ")


@pytest.mark.parametrize("plan, track", [("10-week", "S"), ("8-week", "X"), ("6-week", "S")])
def test_invalid(load, plan, track):
    with pytest.raises(ValueError):
        load("ex01_study_plan").build_plan(plan, track)


def test_render_contains_total(load):
    text = load("ex01_study_plan").render_plan("8-week", "L")
    assert "Total problems: 119" in text
    assert " 6  38-40" in text
