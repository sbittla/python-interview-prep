import pytest


@pytest.mark.parametrize("n", [20, 30, 45, 60, 75, 90, 120])
def test_phases_sum_exactly(load, n):
    plan = load("ex04_interview_day_checklist").phase_plan(n)
    assert sum(plan.values()) == n
    assert list(plan)[0] == "intro" and list(plan)[-1] == "questions"


def test_phase_values(load):
    m = load("ex04_interview_day_checklist")
    assert m.phase_plan(60) == m.BASE_60
    assert m.phase_plan(45) == {"intro": 2, "clarify": 4, "examples": 3, "brute force": 3,
                                "optimise": 5, "code": 17, "test": 7, "questions": 4}


@pytest.mark.parametrize("n", [10, 19, 121])
def test_phase_invalid(load, n):
    with pytest.raises(ValueError):
        load("ex04_interview_day_checklist").phase_plan(n)


def test_checklist_dates(load):
    m = load("ex04_interview_day_checklist")
    rows = m.checklist("2026-12-03 10:00", "virtual")
    assert rows[0] == ("Thu 2026-11-19 10:00", "T-14d",
                       "Start weak-area repair: top 3 areas from the readiness scorer")
    assert rows[-1][0] == "Fri 2026-12-04 10:00" and rows[-1][1] == "T+24h"
    whens = [r[0][4:] for r in rows]
    assert whens == sorted(whens)
    assert any("camera" in r[2] for r in rows)


def test_onsite_and_bad_format(load):
    m = load("ex04_interview_day_checklist")
    rows = m.checklist("2026-12-10 13:30", "onsite")
    assert ("Thu 2026-12-10 12:45", "T-45m", "Arrive 15 minutes early; find the reception") in rows
    with pytest.raises(ValueError):
        m.checklist("2026-12-10 13:30", "phone")


def test_schedule_clock(load):
    sched = load("ex04_interview_day_checklist").phase_schedule("2026-12-03 10:00", 60)
    assert sched[5] == ("10:22", "code", 23)
