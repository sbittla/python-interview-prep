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


def _week_hours(line):
    body = line.split(": ", 1)[1]
    return {k: int(v) for k, v in (p.split("=") for p in body.split(", ") if p)}


def test_weekly_schedule(load):
    m = load("ex02_loop_planner")
    lines = m.weekly_schedule(LOOP, 3, 12)
    assert lines == [
        "Week 1: behavioural=1, coding=7, phone_screen=1, system_design=3",
        "Week 2: behavioural=1, coding=7, phone_screen=1, system_design=3",
        "Week 3: coding=7, phone_screen=2, system_design=3",
    ]


@pytest.mark.parametrize("weeks, per_week", [(1, 5), (3, 12), (4, 7), (5, 1), (6, 13)])
def test_every_week_is_full_and_types_add_up(load, weeks, per_week):
    m = load("ex02_loop_planner")
    weeks_hours = [_week_hours(line) for line in m.weekly_schedule(LOOP, weeks, per_week)]
    assert [sum(w.values()) for w in weeks_hours] == [per_week] * weeks
    plan = m.plan_hours(LOOP, weeks * per_week)
    for kind, hours in plan.items():
        assert sum(w.get(kind, 0) for w in weeks_hours) == hours


def test_repeated_types_merge_before_splitting(load):
    m = load("ex02_loop_planner")
    # coding weight 5 x 2 = 10 vs behavioural 1: merged gives 10/1, not 9/2
    assert m.plan_hours([("coding", 1), ("behavioural", 1), ("coding", 1)], 11) == {
        "behavioural": 1, "coding": 10}
