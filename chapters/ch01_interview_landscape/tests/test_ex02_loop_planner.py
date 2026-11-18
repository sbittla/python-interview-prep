import pytest

LOOP = [("phone_screen", 1), ("coding", 2), ("system_design", 1), ("behavioural", 1)]


def test_example(load):
    m = load("ex02_loop_planner")
    assert m.plan_hours([("coding", 2), ("behavioural", 1)], 10) == {"behavioural": 1, "coding": 9}


@pytest.mark.parametrize("total", [1, 7, 37, 40, 101, 1000])
def test_sums_exactly(load, total):
    m = load("ex02_loop_planner")
    plan = m.plan_hours(LOOP, total)
    assert sum(plan.values()) == total
    assert list(plan) == sorted(plan)


def test_repeated_types_merge(load):
    m = load("ex02_loop_planner")
    assert m.plan_hours([("coding", 1), ("coding", 1)], 9) == {"coding": 9}


def test_unknown_type(load):
    m = load("ex02_loop_planner")
    with pytest.raises(ValueError):
        m.plan_hours([("trivia", 1)], 10)


def test_weekly_schedule(load):
    m = load("ex02_loop_planner")
    lines = m.weekly_schedule(LOOP, 3, 12)
    assert len(lines) == 3
    assert lines[0] == "Week 1: behavioural=1, coding=7, phone_screen=2, system_design=3"
    total = sum(int(p.split("=")[1]) for line in lines for p in line.split(": ")[1].split(", "))
    assert total == 36
